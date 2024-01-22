import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read in coach performance data
coachperf = pd.read_csv('coach_performance.csv')

# Option 1: Coaches by year started with a team
charttype = 'CoachTeam'
# Others to come

# Which teams to use (the first one is for all teams)
selected_teams = coachperf['team'].drop_duplicates().to_frame()
# Only selected conferences
# selected_teams = coachperf.loc[(coachperf['season'] == 2023) & (coachperf['conference'].isin(['A-10','AAC','ACC','Big 12','Big East','Big Ten','MWC','Pac-12','SEC','WCC'])), ['team']].drop_duplicates()
# Only selected teams
# selected_teams = coachperf[coachperf['team'].isin(['NC State', 'LSU'])]['team'].drop_duplicates().to_frame()
# Only one state
# selected_teams = coachperf[coachperf['state'] == 'North Carolina']['team'].drop_duplicates().to_frame()

start = 2010
end = 2023

# Data quality may be poor before 1967 and worse before 1947
for chooseseason in range(start, end + 1):
    
    if charttype == 'CoachTeam':
        perf = coachperf[coachperf['firstseason'] == chooseseason]
        perf['entity'] = perf.apply(lambda row: row['coach'] + '\n' + row['team'] if 'coach' in row else row['team'], axis=1)

    # Subset the teams
    perf = perf[perf['team'].isin(selected_teams['team'])]
    # Optional: Do not show interim coaches
    #vperf = perf[~perf['coachid'].isin(perf.loc[perf['todisplay'] == 'Interim over', 'coachid'].drop_duplicates())]

    # Choose the width and height of the chart based on the number of teams and seasons to display
    graphwidth = 1.90 + 0.93 * (perf['season'].max() - perf['season'].min() + 1)
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
    # Where the border color is white (i.e. non-seasons), replace spaces (after the third position) with new lines
    perf['todisplay'] = np.where(
        perf['bordercolor'] == 'white',
        perf['todisplay'].apply(lambda x: x[:3] + x[3:].replace(' ', '\n')),
        perf['todisplay']
    )
    
    # Sort by score, coach (or team), and season
    perf.sort_values(by=['sumscore', 'entity', 'season'], ascending=[True, False, True], inplace=True)
    perf.reset_index(drop=True, inplace=True)
    
    # Prepare graph with options
    fig, ax = plt.subplots(figsize=(graphwidth, graphheight), dpi=100, layout='constrained')
    
    # Give each season a box with the right starting place and the right color.
    bars = ax.barh(perf['entity'], 1, left = perf['cumulative_widths'] + minseas - 2, color = perf['bgcolor'], edgecolor = perf['bordercolor'])
    
    # For each box, write the text inside near the middle
    i = 0
    for bar in ax.patches:
       ax.text(bar.get_x() + bar.get_width() / 2,
               bar.get_height() / 2 + bar.get_y() -.04,
               perf.at[i,'todisplay'], ha = 'center', va = 'center',
               color = perf.at[i,'fgcolor'], weight = perf.at[i,'fontweight'], size = 12)
       i = i + 1
    
    # Axis, label options
    ax.set_xticks(range(minseas - 1 , minseas + max(perf['cumulative_widths'])))
    ax.tick_params(axis='x', which='both', bottom=True, top=True, labelbottom=True, labeltop=True)
    ax.set_ylabel('Coach')
    ax.set_xlabel('Year')
    ax.margins(x=0.00, y=0.00)
    
    if charttype == 'CoachTeam':
        fig.suptitle(f'Coaches starting with teams in {chooseseason - 1}-{str(chooseseason % 100).zfill(2)}')
        if len(selected_teams) == len(coachperf['team'].drop_duplicates().to_frame()):
            fig.savefig(f'CoachTeamResults{chooseseason}.png')
        else:
            fig.savefig(f'CoachTeamResults{chooseseason}_selected.png')
    
