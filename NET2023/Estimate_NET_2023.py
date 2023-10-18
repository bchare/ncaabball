import pandas as pd
import numpy as np
from sklearn import linear_model

# Read in game stats
games=pd.read_csv('ncaab_stats_input_net_2023.csv')

# Subset to games through Selection Sunday
games=games[games['date']<='2023-03-12']

games['raw_net_eff']=100*(games['points']/(games['fga']-games['orb']+games['tov']+.475*games['fta'])-games['opp_points']/(games['opp_fga']-games['opp_orb']+games['opp_tov']+.475*games['opp_fta']))

# Credit for the ridge regression code (see the link to Colab) goes to
# https://medium.com/analyzing-ncaa-college-basketball-with-gcp/fitting-it-in-adjusting-team-metrics-for-schedule-strength-4e8239be0530

# Make dummy variables for each team and opponent
games_dummy_vars=pd.get_dummies(games[['team', 'opponent', 'hca']])

# Set up ridge regression
reg = linear_model.Ridge(alpha=1, fit_intercept=True)

# Fit ridge regression
reg.fit(
y=games['raw_net_eff'],
X=games_dummy_vars
)

# Extract regression coefficients
net_stats = pd.DataFrame(
{
  'team': games_dummy_vars.columns.values,
  'efficiency': reg.coef_ + reg.intercept_
}
)

# Optional: See the home court advantage (this is the same for all teams)
# home_court_advantage=net_stats[net_stats['team']=='hca']['efficiency'].values[0]
# print("Home Court Advantage is",round(home_court_advantage,2),"Points Per 100 Possessions")

# Only keep rows for the team stats, and rank for this metric
net_stats=net_stats[net_stats['team'].str.startswith('team_')]
net_stats['team']=net_stats['team'].str[5:]
net_stats['efficiency_rank']=net_stats['efficiency'].rank(ascending=False,method='min')

# Neutral games count as 1 game. Home wins & away losses count as 0.6. Home losses & away wins count as 1.4.
conditions=[
    (games['hca']==0),
    ((games['hca']==1) & (games['points']>games['opp_points'])),
    ((games['hca']==-1) & (games['points']<games['opp_points'])),
    ((games['hca']==1) & (games['points']<games['opp_points'])),
    ((games['hca']==-1) & (games['points']>games['opp_points']))
]
values = [1, 0.6, 0.6, 1.4, 1.4]
games['gamevalue']=np.select(conditions, values)
# winvalue is 0 for losses and the gamevalue for wins
games['winvalue']=np.where(games['points']>games['opp_points'],games['gamevalue'],0)

# For each team and opponent, sum the gamevalue and the winvalue
games_sum=games.groupby(['team','opponent'],as_index=False).aggregate({'gamevalue':'sum','winvalue':'sum'})

# For every team, add a win and a loss against a fictional team
# (Without this, winless teams would have zero value and undefeated teams would have infinite value)
fiction_sum=pd.DataFrame(games['team'].unique(), columns=['team']) 
fiction_sum['opponent']='ZZZ_FICTIONAL'
fiction_sum['gamevalue']=2
fiction_sum['winvalue']=1
games_sum=pd.concat([games_sum, fiction_sum])
fiction_sum=pd.DataFrame(games['team'].unique(), columns=['opponent']) 
fiction_sum['team']='ZZZ_FICTIONAL'
fiction_sum['gamevalue']=2
fiction_sum['winvalue']=1
games_sum=pd.concat([games_sum, fiction_sum])

# Credit for the Bradley-Terry ranking code goes to
# https://datascience.oneoffcoder.com/btl-model.html

# Make a 364x364 table of how often everybody beat everybody
teams = sorted(list(set(games_sum.team) | set(games_sum.opponent)))
t2i = {t: i for i, t in enumerate(teams)}
games_sum['r'] = games_sum['team'].apply(lambda t: t2i[t])
games_sum['c'] = games_sum['opponent'].apply(lambda t: t2i[t])
n_teams = len(teams)
mat = np.zeros([n_teams, n_teams])
for _, r in games_sum.iterrows():
    mat[r.r, r.c] = r.winvalue
creditmatrix = pd.DataFrame(mat, columns=teams, index=teams)

# Iteratively use the large table to assign a maximum likelihood value to each team
def get_estimate(i, p, df):
    get_prob = lambda i, j: np.nan if i == j else p.iloc[i] + p.iloc[j]
    n = df.iloc[i].sum()
    d_n = df.iloc[i] + df.iloc[:, i]
    d_d = pd.Series([get_prob(i, j) for j in range(len(p))], index=p.index)
    d = (d_n / d_d).sum()
    return n / d
def estimate_p(p, df):
    return pd.Series([get_estimate(i, p, df) for i in range(df.shape[0])], index=p.index)
def iterate(df, p=None, n=100, sorted=True):
    if p is None:
        p = pd.Series([1 for _ in range(df.shape[0])], index=list(df.columns))
    for _ in range(n):
        p = estimate_p(p, df)
        p = p / p.sum()
    p = p.sort_values(ascending=False) if sorted else p
    return p
p = iterate(creditmatrix)

# Remove the fictional team, scale the scores to an average of 1, rank the teams
teamvalue=p.to_frame().reset_index()
teamvalue.rename(columns={'index': 'team', 0: 'value'},inplace=True)
teamvalue=teamvalue[teamvalue['team'] != 'ZZZ_FICTIONAL']
teamvalue['value']=teamvalue['value']*teamvalue['value'].count()/teamvalue['value'].sum()
teamvalue['value_rank']=teamvalue['value'].rank(ascending=False,method='min')

# Combine efficiency and value metrics and make an estimated NET ranking (Count Efficiency 80% and Value 20%)
net_stats=net_stats.merge(teamvalue,on='team')
net_stats['estimated_net']=0.8*net_stats['efficiency_rank']+0.200001*net_stats['value_rank']
net_stats['estimated_net']=net_stats['estimated_net'].rank(method='min')
net_stats.sort_values(by='estimated_net', inplace=True)
net_stats['efficiency_rank'] = net_stats['efficiency_rank'].astype(int) 
net_stats['value_rank'] = net_stats['value_rank'].astype(int) 
net_stats['estimated_net'] = net_stats['estimated_net'].astype(int) 

print(net_stats.to_string(columns=['estimated_net','team','efficiency','value'], index=False))

# net_stats.to_csv('net_estimate_output_selection_sunday_2023.csv', index=False)
