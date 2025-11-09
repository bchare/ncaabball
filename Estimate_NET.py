import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
import scipy.stats

# Read in game stats
games = pd.read_csv('ncaab_stats_input_2026.csv')

# Subset to games before a certain date
# games = games[games['date'] <= '2026-03-15']

# Credit for the ridge regression code (see the link to Colab) goes to:
# https://medium.com/analyzing-ncaa-college-basketball-with-gcp/fitting-it-in-adjusting-team-metrics-for-schedule-strength-4e8239be0530

# Calculate the scoring margin in points per 100 possessions
games['raw_net_eff'] = 100*(games['points']/(games['fga']-games['orb']+games['tov']+.475*games['fta'])-games['opp_points']/(games['opp_fga']-games['opp_orb']+games['opp_tov']+.475*games['opp_fta']))
# games['off_eff'] = 100*(games['points']/(games['fga']-games['orb']+games['tov']+.475*games['fta']))
# games['def_eff'] = 100*(games['opp_points']/(games['opp_fga']-games['opp_orb']+games['opp_tov']+.475*games['opp_fta']))
# games['avg_pos'] = 0.5*((games['fga']-games['orb']+games['tov']+.475*games['fta'])+(games['opp_fga']-games['opp_orb']+games['opp_tov']+.475*games['opp_fta']))

# Make dummy variables for each team and opponent
games_dummy_vars = pd.get_dummies(games[['team', 'opponent', 'hca']])

# Ridge regression (for Efficiency)
reg = linear_model.Ridge(alpha=1, fit_intercept=True)
reg.fit(y=games['raw_net_eff'], X=games_dummy_vars)
net_stats = pd.DataFrame({'team': games_dummy_vars.columns.values, 'efficiency': reg.coef_ + reg.intercept_})

# Optional: See the home court advantage (this is the same for all teams)
home_court_advantage=net_stats[net_stats['team'] == 'hca']['efficiency'].values[0]
print("Home Court Advantage is", round(home_court_advantage,2), "Points Per 100 Possessions")

# Only keep rows for the team stats
net_stats = net_stats[net_stats['team'].str.startswith('team_')]
net_stats['team'] = net_stats['team'].str[5:]

# Calculate rating, ranking, and normalized score
net_stats['efficiency_rtg'] = 100*scipy.stats.norm.cdf(net_stats['efficiency'], net_stats['efficiency'].mean(), net_stats['efficiency'].std())
net_stats['efficiency_rank'] = net_stats['efficiency'].rank(ascending=False, method='min')
eff_min = net_stats['efficiency'].min()
eff_max = net_stats['efficiency'].max()
net_stats['efficiency_norm'] = (net_stats['efficiency'] - eff_min) / (eff_max - eff_min + 1e-6)

# Credit for the Bradley-Terry ranking code goes to:
# https://datascience.oneoffcoder.com/btl-model.html

# Give each team a win and a loss against a fake team (this prevents a large difference between winless and undefeated teams)
fiction = pd.DataFrame(games['team'].unique(), columns=['team']) 
fiction['opponent'] = 'ZZZ_FICTIONAL'
fiction['hca'] = 0
fiction['points'] = 100
fiction['opp_points'] = 101
games = pd.concat([games, fiction])
fiction['opp_points'] = 99
games = pd.concat([games, fiction])
games = games.reset_index()

# Make a list of unique teams
teams = sorted(list(set(games.team) | set(games.opponent)))

# Prepare a series of output (0/1 for loss/win) and a dataframe of input (1 row per game, 1 column per team)
def get_vector(r):
    y = {'y': 1 if r.points > r.opp_points else 0}
    v = {t: 0 for t in teams}
    v[r.team] = 1
    v[r.opponent] = -1
    return {**y, **v}

X = pd.DataFrame(list(games.apply(get_vector, axis=1)))
y = X.y
X = X[[c for c in X.columns if c != 'y']]
# Also use home court advantage as an input
X['hca'] = games['hca']

# Logistic regression (for Value)
log = LogisticRegression(penalty=None, fit_intercept=False)
log.fit(X, y)
teamvalue = sorted(list(zip(X.columns, log.coef_[0])), key=lambda tup: tup[1], reverse=True)
teamvalue = pd.Series([c for _, c in teamvalue], index=[t for t, _ in teamvalue])
teamvalue = teamvalue.to_frame().reset_index()
teamvalue.rename(columns={'index': 'team', 0: 'value'}, inplace=True)
# Drop the fictional team and home court advantage
teamvalue = teamvalue[teamvalue['team'] != 'ZZZ_FICTIONAL']
teamvalue = teamvalue[teamvalue['team'] != 'hca']

# Calculate rating, ranking, and normalized score
teamvalue['value_rtg'] = 100*scipy.stats.norm.cdf(teamvalue['value'], teamvalue['value'].mean(), teamvalue['value'].std())
teamvalue['value_rank'] = teamvalue['value'].rank(ascending=False, method='min')
val_min = teamvalue['value'].min()
val_max = teamvalue['value'].max()
teamvalue['value_norm'] = (teamvalue['value'] - val_min) / (val_max - val_min + 1e-6)

# Combine efficiency and value numbers
net_stats = net_stats.merge(teamvalue,on='team')
# Combine the normalized efficiency (worth 80%) and normalized value (worth 20%) and rank
net_stats['estimated_net'] = (0.8 * net_stats['efficiency_norm'] + 0.2 * net_stats['value_norm']).rank(ascending=False, method='min')
net_stats.sort_values(by='estimated_net', inplace=True)

# Turn ranks into integers
net_stats['efficiency_rank'] = net_stats['efficiency_rank'].astype(int)
net_stats['value_rank'] = net_stats['value_rank'].astype(int) 
net_stats['estimated_net'] = net_stats['estimated_net'].astype(int) 
# Put the estimated rank first
net_stats.insert(0, 'estimated_net', net_stats.pop('estimated_net'))

# print(net_stats.to_string(columns=['estimated_net','team','efficiency_rtg','value_rtg'], index=False))

net_stats.to_csv('estimated_net_output.csv', index=False)

