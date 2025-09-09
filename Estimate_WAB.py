import pandas as pd
from sklearn import linear_model

# Input game results
games = pd.read_csv('ncaab_stats_input_2025.csv')

# Subset to games by Selection Sunday
games = games[games['date'] <= '2025-03-16']

# For each game, calculate offensive and defensive efficiency (points per 100 possessions)
games['off_eff'] = 100*(games['points']/(games['fga']-games['orb']+games['tov']+.475*games['fta']))
games['def_eff'] = 100*(games['opp_points']/(games['opp_fga']-games['opp_orb']+games['opp_tov']+.475*games['opp_fta']))

# For each game, make True/False fields for each team involved
games_dummy_vars = pd.get_dummies(games[['team', 'opponent']])

# For each team, get an opponent-adjusted offensive efficiency
reg_off = linear_model.Ridge(alpha=1, fit_intercept=True)
reg_off.fit(y=games['off_eff'], X=games_dummy_vars)
off_stats = pd.DataFrame({'team': games_dummy_vars.columns.values, 'off_eff': reg_off.coef_ + reg_off.intercept_})

# For each team, get an opponent-adjusted defensive efficiency
reg_def = linear_model.Ridge(alpha=1, fit_intercept=True)
reg_def.fit(y=games['def_eff'], X=games_dummy_vars)
def_stats = pd.DataFrame({'team': games_dummy_vars.columns.values, 'def_eff': reg_def.coef_ + reg_def.intercept_})

# Combine both results
wab_stats = off_stats.merge(def_stats, on='team')
wab_stats = wab_stats[wab_stats['team'].str.startswith('team_')]
wab_stats['team'] = wab_stats['team'].str[5:]

# Calculate team strength using Pythagorean expectation with exponent 11.5
wab_stats['pythag'] = (wab_stats['off_eff'] ** 11.5) / ((wab_stats['off_eff'] ** 11.5) + (wab_stats['def_eff'] ** 11.5))
# Rank by strength
wab_stats['pythag_rank'] = wab_stats['pythag'].rank(ascending=False, method='min').astype(int)

# Need to input the NET rankings
realnet = pd.read_table('actual_net_20250316.txt')
wab_stats = wab_stats.merge(realnet[['Team', 'NET Rank']], 
    left_on='team', 
    right_on='Team', 
    how='left').drop('Team', axis=1)

# Team strengths must be put in order of the NET rankings
# Also define the bubble strength as the average of the 44th, 45th, and 46th teams
wab_stats = wab_stats.merge(
    wab_stats[['pythag_rank', 'off_eff', 'def_eff', 'pythag']], 
    how='left', 
    left_on='NET Rank', 
    right_on='pythag_rank', 
    suffixes=('', '_rerank')
).drop(columns='pythag_rank_rerank').assign(
    bubble_off=lambda x: x[x['pythag_rank'].between(44, 46)]['off_eff'].mean(),
    bubble_def=lambda x: x[x['pythag_rank'].between(44, 46)]['def_eff'].mean()
)

# For each game, get the offensive and defensive numbers for the opponent and the bubble team
gamewab = games[['team', 'opponent', 'date', 'hca', 'points', 'opp_points']].merge(
    wab_stats[['team', 'off_eff_rerank', 'def_eff_rerank', 'NET Rank', 'bubble_off', 'bubble_def']], 
    left_on='opponent', right_on='team').drop('team_y', axis=1).rename(
    columns={'team_x': 'team'})

# For home games, assume the hypothetical bubble team will play better and the opponent will play worse
gamewab.loc[gamewab['hca'] == 1, ['def_eff_rerank', 'bubble_off']] = gamewab.loc[gamewab['hca'] == 1, ['def_eff_rerank', 'bubble_off']] * 1.013
gamewab.loc[gamewab['hca'] == 1, ['off_eff_rerank', 'bubble_def']] = gamewab.loc[gamewab['hca'] == 1, ['off_eff_rerank', 'bubble_def']] * 0.987
# For away games, assume the hypothetical bubble team will play worse and the opponent will play better
gamewab.loc[gamewab['hca'] == -1, ['def_eff_rerank', 'bubble_off']] = gamewab.loc[gamewab['hca'] == -1, ['def_eff_rerank', 'bubble_off']] * 0.987
gamewab.loc[gamewab['hca'] == -1, ['off_eff_rerank', 'bubble_def']] = gamewab.loc[gamewab['hca'] == -1, ['off_eff_rerank', 'bubble_def']] * 1.013

# Calculate team strength using Pythagorean expectation with the home/away adjustments
gamewab['pythag_rerank'] = (gamewab['off_eff_rerank'] ** 11.5) / (gamewab['off_eff_rerank'] ** 11.5 + gamewab['def_eff_rerank'] ** 11.5)
gamewab['pythag_bubble'] = (gamewab['bubble_off'] ** 11.5) / (gamewab['bubble_off'] ** 11.5 + gamewab['bubble_def'] ** 11.5)

# Use the Log5 formula to find the probability that the opponent would beat the bubble team. This is the game's WAB value.
gamewab['game_wab'] = (gamewab['pythag_rerank'] * (1 - gamewab['pythag_bubble'])) / (gamewab['pythag_rerank'] * (1 - gamewab['pythag_bubble']) + gamewab['pythag_bubble'] * (1 - gamewab['pythag_rerank']))

# For a win, increase the team's WAB by that value. For a loss, add the same value and subtract 1.
gamewab.loc[gamewab['points'] < gamewab['opp_points'], 'game_wab'] = gamewab.loc[gamewab['points'] < gamewab['opp_points'], 'game_wab'] - 1

# Sum the values by team
wab_results = gamewab.groupby('team')['game_wab'].sum().reset_index().rename(columns={'game_wab': 'Est_WAB'})

# Compare the calculated results to the NCAA's WAB
wab_results = wab_results.merge(realnet[['Team', 'WAB']], how='left', left_on='team', right_on='Team').drop('Team', axis=1)
wab_results['WAB_diff'] = wab_results['Est_WAB'] - wab_results['WAB']

# Export results with estimated vs. actual WAB
wab_results.to_csv('estimated_wab_output_2025.csv', index=False)

# Preparing a report of WAB impact per game, sort by team and date
game_impact_wab = gamewab.sort_values(by=['team', 'date'])

# Calculate cumulative WAB values by team through that date
game_impact_wab['cum_game_wab'] = game_impact_wab.groupby('team')['game_wab'].cumsum()

# Generate descriptions (e.g. "2025-02-22  Home win      #69 Wake Forest          0.224  -7.655")
game_impact_wab['description'] = game_impact_wab.apply(
    lambda x: (
        outcome := f"{'Away' if x['hca'] == -1 else 'Home' if x['hca'] == 1 else 'Neutral'} "
                   f"{'win' if x['points'] > x['opp_points'] else 'loss'}",
        f"{x['date']}  {outcome + ' ' * (12 - len(outcome))} {'#' + str(x['NET Rank']):>4} {x['opponent']:<19} {x['game_wab']:>6.3f} {x['cum_game_wab']:>7.3f}"
    )[1], axis=1
)

# Add the actual WAB values for comparison
game_impact_wab = game_impact_wab.merge(realnet[['Team', 'WAB']], how='left', left_on='team', right_on='Team').drop('Team', axis=1)

# Generate a text file with a report of WAB impact per game
with open('game_impact_wab_2025.txt', 'w') as f:
    f.write('----------------------------------------------------------------\n')
    for team, group in game_impact_wab.groupby('team'):
        f.write(f"2025 Estimated WAB - {team}\n")
        f.write("Date:       Result:           Opponent:           Value:    Sum:\n")
        for desc in group['description']:
            f.write(f"{desc}\n")
        wab_str = f"{group['WAB'].iloc[0]:.2f}"
        spaces = ' ' * (63 - len("Actual NCAA WAB on Selection Sunday:") - len(wab_str))
        f.write(f"Actual NCAA WAB on Selection Sunday:{spaces}{wab_str}\n")
        f.write('----------------------------------------------------------------\n')
