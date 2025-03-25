import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read in coach performance data
try:
    coachperf = pd.read_csv('coach_performance.csv')
except:
    print("No coach_performance.csv file")

# # Read in coach Candidates data
# try:
#     targets = pd.read_csv('coach_targets.csv')
# except:
#     print("No coach_targets.csv file")
    
# Read in team performance data
try:
    teamperf = pd.read_csv('team_performance.csv')
except:
    print("No team_performance.csv file")

# Option 1: All coaches starting with a team in season (year)
charttype = 'CoachTeamHireClass'
# chooseseason = 2018
start = 1996
end = 2025
start = 2013
end = 2013

# Option 2: Coach candidates
# charttype = 'CoachCandidates'
# chooseseason = 2017
# chooseteam = 'NC State'
# chooseseason = 2017
# chooseteam = 'Oklahoma St.'
# chooseseason = 2019
# chooseteam = 'Vanderbilt'
# chooseseason = 2016
# chooseteam = 'Stanford'

# Option 3: Best teams in timeframe (needs work)
# charttype = 'TeamBestFirst'
# start = 2025
# end = 2025

# Option 4: Best coaches in timeframe (need work)
# charttype = 'CoachBestFirst'
# start = 2021
# end = 2025

# Option 5: Selected coaches
# charttype = 'SelectedCoach'
# coaches_str = """
# """
# coaches_list = coaches_str.split('\n')
# coachlist = pd.DataFrame({'coachid': coaches_list,'order': range(1, len(coaches_list) + 1)})
# start = 2021
# end = 2025

# Others to come

# Which teams to use (the first one is for all teams)
selected_teams = coachperf['team'].drop_duplicates().to_frame()
# Only selected conferences
# selected_teams = coachperf.loc[(coachperf['season'] == 2023) & (coachperf['conference'].isin(['A-10','AAC','ACC','Big 12','Big East','Big Ten','MWC','Pac-12','SEC','WCC'])), ['team']].drop_duplicates()
# selected_teams = coachperf.loc[(coachperf['season'] == 2023) & (coachperf['conference'].isin(['ACC'])), ['team']].drop_duplicates()
# Only selected teams
# selected_teams = coachperf[coachperf['team'].isin(['NC State', 'LSU'])]['team'].drop_duplicates().to_frame()
# Only one state
# selected_teams = coachperf[coachperf['state'] == 'North Carolina']['team'].drop_duplicates().to_frame()

# For no loop
# if True:
# Optional: 'CoachTeamHireClass' graphs by year (data quality may be poor before 1967 and worse before 1947)
for chooseseason in range(start, end + 1):
    
    if charttype == 'CoachTeamHireClass':
        perf = coachperf[coachperf['firstseason'] == chooseseason]
        perf['entity'] = perf.apply(lambda row: row['coach'] + '\n' + row['team'] if 'coach' in row else row['team'], axis=1)
        
    if charttype == 'CoachCandidates':
        targetssub = targets[(targets['team'] == chooseteam) & (targets['lookingyear'] == chooseseason)]
        targetssub.drop('team', axis=1, inplace=True)
        source = targetssub.iloc[-1]['coachid']
        # perf = coachperf[(coachperf['team'] == chooseteam) & (coachperf['season'] == (chooseseason + 1)) & (coachperf['season'] > (chooseseason - 3)) & (coachperf['isseason'] > 0)]
        # perf['order'] = 0
        perf = coachperf[(coachperf['season'] > (chooseseason - 3)) & (coachperf['isseason'] > 0)]
        # perf = pd.concat([perf, mostperf], ignore_index=True)
        # perf = perf.drop_duplicates(subset=['coachid', 'season'], keep='first')
        perf = perf.merge(targetssub, on='coachid')
        actualhire = coachperf[(coachperf['team'] == chooseteam) & (coachperf['season'] == (chooseseason + 1)) & (coachperf['season'] > (chooseseason - 3)) & (coachperf['isseason'] > 0)]
        actualhire['order'] = 0
        perf = pd.concat([actualhire, perf], ignore_index=True)
        perf['entity'] = perf['coach']
        entities = perf['entity'].unique()
        season_range = range(min(perf['season']), max(perf['season']) + 1)
        combinations = pd.DataFrame([(entity, season) for entity in entities for season in season_range], columns=['entity', 'season'])
        combinations['team'] = ''
        combinations['todisplay'] = ''
        combinations['bgcolor'] = '#FFFFFF'
        combinations['fgcolor'] = '#000000'
        combinations['bordercolor'] = '#FFFFFF'
        perf = pd.concat([perf, combinations], ignore_index=True)
        perf = perf.sort_values(by=['entity', 'season'])
        perf = perf.drop_duplicates(subset=['entity', 'season'], keep='first')
        perf['order'] = perf.groupby('entity')['order'].transform('min')        
        perf.sort_values(by=['order', 'season'], ascending=[False, True], inplace=True)

    if charttype == 'SelectedCoach':
        perf = coachperf[(coachperf['season'].between(start, end)) & (coachperf['isseason'] > 0) & ((coachperf['season'] - coachperf['firstseason']) < 99)]
        perf = perf.merge(coachlist[['coachid','order']], how='inner', on='coachid')
        perf['entity'] = perf.apply(lambda row: '\n'.join([str(perf[(perf['coachid'] == row['coachid']) & (perf['season'] == perf[perf['coachid'] == row['coachid']]['season'].max())]['coach'].values[0]), 
        perf[(perf['coachid'] == row['coachid']) & (perf['season'] == perf[perf['coachid'] == row['coachid']]['season'].max())]['team'].values[0]]) 
        if row['coachid'] in perf[perf['season'] == perf.groupby('coachid')['season'].transform("max")]['coachid'].values 
        else row['team'], axis=1)
        
        entities = perf['entity'].unique()
        season_range = range(min(perf['season']), max(perf['season']) + 1)
        combinations = pd.DataFrame([(entity, season) for entity in entities for season in season_range], columns=['entity', 'season'])
        combinations['team'] = ''
        combinations['todisplay'] = ''
        combinations['bgcolor'] = '#FFFFFF'
        combinations['fgcolor'] = '#000000'
        combinations['bordercolor'] = '#FFFFFF'
        perf = pd.concat([perf, combinations], ignore_index=True)
        perf = perf.sort_values(by=['entity', 'season'])
        perf = perf.drop_duplicates(subset=['entity', 'season'], keep='first')
        perf['order'] = perf.groupby('entity')['order'].transform(lambda x: x.max() if (perf['isseason'] > 2).any() else x.max() if x.max() else None)
        perf.sort_values(by=['order', 'season'], ascending=[False, True], inplace=True)




    if charttype == 'TeamBestFirst':
        perf = teamperf[(teamperf['season'] >= start) & (teamperf['season'] <= end)]
        perf['entity'] = perf['team']
        perf['bordercolor'] = 'black'
        perf['sumscore'] = perf.groupby('entity')['score'].transform('sum')
        perf['isseason'] = 4
        perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[False, True, False], inplace=True)
        perf['entnum'] = (perf['entity'] != perf['entity'].shift()).cumsum()
        perf = perf[perf['entnum'] <= 100]
        perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[True, False, True], inplace=True)

    if charttype == 'CoachBestFirst':
        coachperf['firstseason'] = pd.to_numeric(coachperf['firstseason'], errors='coerce')
        coachperf['season'] = pd.to_numeric(coachperf['season'], errors='coerce')

        perf = coachperf[(coachperf['season'].between(start, end)) & 
                        ((coachperf['season'] - coachperf['firstseason']) < 99)]
        perf['entity'] = perf.apply(lambda row: row['coach'] + '\n' + row['team'] if 'coach' in row else row['team'], axis=1)
        # perf['entity'] = perf['coach']
        perf['sumscore'] = perf.groupby('entity')['score'].transform('sum')
        perf['numseas'] = perf.groupby('entity')['isseason'].transform(lambda x: (x > 1).sum())
        perf = perf[perf['numseas'] == 3]
        perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[False, True, False], inplace=True)
        perf['entnum'] = (perf['entity'] != perf['entity'].shift()).cumsum()
        perf = perf[perf['entnum'] <= 100]
        perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[True, False, True], inplace=True)


    if charttype != 'CoachCandidates' and charttype != 'TeamBestFirst' and charttype != 'SelectedCoach':
        # Subset the teams
        perf = perf[perf['team'].isin(selected_teams['team'])]
        # Optional: Do not show interim coaches
        perf = perf[~perf['coachid'].isin(perf.loc[perf['todisplay'] == 'Interim over', 'coachid'].drop_duplicates())]        
        perf = perf[~perf['coachid'].isin(perf.loc[perf['todisplay'] == 'Interim', 'coachid'].drop_duplicates())]        

    # Choose the width and height of the chart based on the number of teams and seasons to display
    graphwidth = 2.10 + 0.93 * (perf['season'].max() - perf['season'].min() + 1)
    graphheight = 1.25 + 0.49 * (perf['entity'].nunique())
    
    # Save the minimum season. Every year has a width of 1.
    minseas = perf['season'].min()
    perf['width']=1
    
    # Sum the widths like this to get them to display right.
    cumu_widths = perf.groupby('entity')['width'].transform(pd.Series.cumsum)
    perf['cumulative_widths'] = cumu_widths
    # Champions get bold text
    perf['fontweight'] = perf.apply(lambda row: 'bold' if 'Champion' in row['todisplay'] else 'regular', axis=1)
    # Sum the score for each coach (or team)
    perf['sumscore'] = perf.groupby('entity')['score'].transform('sum')
    perf['last_season'] = perf.groupby('entity')['season'].transform(lambda x: x.max() if (perf['isseason'] > 2).any() else x.max() if x.max() else None)
    perf['last_season'] = perf.groupby('entity')['last_season'].transform(lambda x: x - 1.5 if (perf.loc[x.index, 'isseason'] == 0).any() else x)
    # perf['last_season'] = perf.groupby('entity').apply(lambda group: group.loc[group['isseason'] > 2, 'season'].max() if (group['isseason'] > 2).any() else group['season'].max())
    # perf['last_season'] = perf.groupby('entity').apply(lambda x: x.loc[x['isseason'] > 2, 'season'].max() if (x['isseason'] > 2).any() else None)

    # Where the border color is white (i.e. non-seasons), replace spaces (after the third position) with new lines
    perf['todisplay'] = np.where(
        perf['bordercolor'] == 'white',
        perf['todisplay'].apply(lambda x: x[:3] + x[3:].replace(' ', '\n')),
        perf['todisplay']
    )

    if charttype == 'CoachTeamHireClass':
        # Sort by score, coach (or team), and season
        # perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[True, False, True], inplace=True)
        perf.sort_values(by=['last_season','sumscore', 'entity', 'season'], ascending=[True, True, False, True], inplace=True)
        # perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[True, False, True], inplace=True)

        # perf = pd.merge(combinations, perf, on=['entity', 'season'], how='left').drop_duplicates().sort_values(by=['entity', 'season']).reset_index(drop=True)
        # perf.sort_values(by=['order', 'season'], ascending=[False, True], inplace=True)

    perf.reset_index(drop=True, inplace=True)
    
    # Prepare graph with options
    fig, ax = plt.subplots(figsize=(graphwidth, graphheight), dpi=100, layout='constrained')
    
    # Give each season a box with the right starting place and the right color.
    bars = ax.barh(perf['entity'], 1, left = perf['cumulative_widths'] + minseas - 2, color = perf['bgcolor'], edgecolor = perf['bordercolor'], height=0.7)
    
    # For each box, write the text inside near the middle
    i = 0
    for bar in ax.patches:
       ax.text(bar.get_x() + bar.get_width() / 2,
               bar.get_height() / 2 + bar.get_y() - 0.04,
               perf.at[i,'todisplay'], ha = 'center', va = 'center',
               color = perf.at[i,'fgcolor'], weight = perf.at[i,'fontweight'], size = 11)
       if charttype == 'CoachCandidates' or charttype == 'SelectedCoach':
           ax.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() / 2 + bar.get_y() + 0.45,
                   perf.at[i,'team'], ha = 'center', va = 'center',
                   color = 'black', size = 7)
           if perf.at[i,'nextyear'] in (['Fired','Scandal','Health','Resigned','Interim','Retired']):
               ax.text(bar.get_x() + bar.get_width() * 0.95,
                       bar.get_height() / 2 + bar.get_y(),
                       perf.at[i,'nextyear'], ha = 'center', va = 'center',
                       color = 'red', size = 7, rotation = 90,
                       bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))
       i = i + 1

    # Axis, label options
    ax.set_xticks(range(minseas - 1 , minseas + max(perf['cumulative_widths'])))
    ax.tick_params(axis='x', which='both', bottom=True, top=True, labelbottom=True, labeltop=True)
    ax.set_ylabel('Coach')
    ax.set_xlabel('Year')
    if charttype == 'CoachCandidates':
        ax.set_xlabel(' ')
    ax.margins(x=0.00, y=0.00)
    ax.set_ylim(-0.4, perf['entity'].nunique() - 0.35)
    if charttype == 'CoachCandidates':
        ax.axvline(x=chooseseason, color='black', linestyle='solid', linewidth=3)
    
    if charttype == 'CoachTeamHireClass':
        fig.suptitle(f'Coaches starting with teams in {chooseseason - 1}-{str(chooseseason % 100).zfill(2)}')
        if len(selected_teams) == len(coachperf['team'].drop_duplicates().to_frame()):
            fig.savefig(f'CoachTeamResults{chooseseason}.png')
        else:
            fig.savefig(f'CoachTeamResults{chooseseason}_selected.png')

    if charttype == 'CoachCandidates':
        fig.suptitle(f'Likely Candidates for {chooseteam} in {chooseseason}\nResults before & after that coaching search')
        plt.figtext(0.5, 0.005, "Source: " + source, ha='center', fontsize=10, color='black')
        fig.savefig(f'CoachCandidates_{chooseteam}_{chooseseason}.png')
    
    if charttype == 'TeamBestFirst':
        fig.savefig('TeamBestFirst.png')
            
    if charttype == 'CoachBestFirst':
        fig.savefig('CoachBestFirst.png')
            
    if charttype == 'SelectedCoach':
        # fig.suptitle('Coaches Most Likely To Be FIRED\n(According to my janky recurrent neural network)')
        fig.suptitle('Coaches Most Likely To TAKE ANOTHER JOB\n(According to my janky recurrent neural network)')        
        # fig.savefig('SelectedCoach.png')
        fig.savefig('MostLikelyLeave.png')
        
# perf.to_csv('perf.csv', index=False)
