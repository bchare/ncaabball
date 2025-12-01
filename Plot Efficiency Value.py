import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

season = 2026

# Read the output from "Estimate NET.py"
net_stats = pd.read_csv('estimated_net_output.csv')

# For the graph title, use the list of games to find the most recent date
try:
    games = pd.read_csv(f'ncaab_stats_input_{season}.csv')
    maxdate = games['date'].max()
except:
    maxdate = str(season)

# Recommended: Add team colors
try:
    teamcolors = pd.read_csv('teamcolors.csv')
    net_stats = net_stats.merge(teamcolors, on='team')
except:
    net_stats['bgcolor'] = '#000000'

# If you have logos for every team, point to them
try:
    teamlogos = pd.read_csv('teamlogos.csv')
    logoseason = 2026
    override_tag = None  # Set to 'fun', 'alt', 'random', or None for normal (no override)
    if override_tag == 'random':
        teamlogos = teamlogos.groupby('team').sample(n=1, random_state=np.random.randint(0, 10000))
    elif override_tag:
        teamlogos['is_override'] = (teamlogos['tag'] == override_tag).astype(int)
        teamlogos = teamlogos.sort_values(by=['team', 'is_override', 'thruyear'], ascending=[True, False, True])
        teamlogos = teamlogos.groupby('team').head(1).drop(columns=['is_override'])
    else:
        teamlogos = teamlogos[teamlogos['thruyear'] >= logoseason]
        teamlogos = teamlogos.loc[teamlogos.groupby('team')['thruyear'].idxmin()]
    teamlogos['logo'] = '.\\logos\\'+teamlogos['logo']
    net_stats = net_stats.merge(teamlogos, on='team')
    net_stats['to_display'] = '#' + net_stats['estimated_net'].astype(str)
    havelogos = 1
except:
    net_stats['to_display'] = '#' + net_stats['estimated_net'].astype(str) + ' ' + net_stats['team']
    havelogos = 0

def makeplot(title, condition):
    # Sorting them this way puts circles for the #1 team over others
    net_stats.sort_values(by='estimated_net', ascending=False, inplace=True)
    net_stats['visibility'] = net_stats.eval(condition).astype(int)
    net_stats_subset=net_stats[net_stats['visibility']==1]
    x_visible = net_stats.loc[net_stats['visibility']==1, 'value_norm']
    y_visible = net_stats.loc[net_stats['visibility']==1, 'efficiency_norm']
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100, layout='constrained')
    fig.suptitle(('Estimated NET - ' + title + '\n(Games Through ' + maxdate + ')').strip())
    ax.scatter(net_stats['value_norm'], net_stats['efficiency_norm'], 100, net_stats['bgcolor'], alpha=0.05*(1-net_stats['visibility']))
    if havelogos == 1:
        for i in net_stats_subset.index:
            ax.annotate(net_stats_subset.at[i,'to_display'], xy=(net_stats_subset.at[i,'value_norm'], net_stats_subset.at[i,'efficiency_norm']), ha='center', va='bottom', xytext=(0, 15), textcoords='offset points', zorder=5000)
            ax.add_artist(AnnotationBbox(OffsetImage(plt.imread(net_stats_subset.at[i,'logo']), zoom=0.333), (net_stats_subset.at[i,'value_norm'], net_stats_subset.at[i,'efficiency_norm']), frameon=False))
    else:
        ax.scatter(net_stats_subset['value_norm'], net_stats_subset['efficiency_norm'], 100, net_stats_subset['bgcolor'], alpha=1)
        for i in net_stats_subset.index:
            ax.annotate(net_stats_subset.at[i,'to_display'], xy=(net_stats_subset.at[i,'value_norm'], net_stats_subset.at[i,'efficiency_norm']), ha='center', va='bottom', xytext=(0, 6), textcoords='offset points', zorder=5000)
    ax.set_ylabel('Strength')
    ax.set_xlabel('Resume')
    pad = 0.02  # small padding so points aren't on the edge
    ax.set_xlim(x_visible.min() - pad, x_visible.max() + pad)
    ax.set_ylim(y_visible.min() - pad, y_visible.max() + pad)
    fig.savefig(f'NET Scatter {title}.png')


# makeplot("All Teams", "estimated_net <= 999")
makeplot("Top 25", "estimated_net <= 25")
makeplot("Top 50", "estimated_net <= 50")
# makeplot("Top 75", "estimated_net <= 75")
makeplot("Top 100", "estimated_net <= 100")

makeplot("ACC", 'team.isin(["Boston College","California","Clemson","Duke","Florida St.","Georgia Tech","Louisville","Miami (FL)","NC State","North Carolina","Notre Dame","Pittsburgh","SMU","Stanford","Syracuse","Virginia","Virginia Tech","Wake Forest"])')
makeplot("Big 12", 'team.isin(["Arizona","Arizona St.","Baylor","BYU","Cincinnati","Colorado","Houston","Iowa St.","Kansas","Kansas St.","Oklahoma St.","TCU","Texas Tech","UCF","Utah","West Virginia"])')
makeplot("SEC", 'team.isin(["Alabama","Auburn","Arkansas","Florida","Georgia","Kentucky","LSU","Mississippi St.","Missouri","Ole Miss","Oklahoma","South Carolina","Tennessee","Texas","Texas A&M","Vanderbilt"])')
makeplot("Big Ten", 'team.isin(["Illinois","Indiana","Iowa","Maryland","Michigan","Michigan St.","Minnesota","Nebraska","Northwestern","Ohio St.","Oregon","Penn St.","Purdue","Rutgers","Southern California","UCLA","Washington","Wisconsin"])')
makeplot("Big East", 'team.isin(["Butler","Creighton","DePaul","Georgetown","Marquette","Providence","Seton Hall","St. John\'s (NY)","UConn","Villanova","Xavier"])')


# makeplot("NC Teams", "state == 'North Carolina'")