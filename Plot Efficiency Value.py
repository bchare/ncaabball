import pandas as pd
import numpy as np
# import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import math

season = 2024

# Read the output from "Estimate NET.py"
net_stats = pd.read_csv('estimated_net_output.csv')

# Input the real NET values
realnet = pd.read_table('actual_net.csv')
net_stats = pd.merge(net_stats, realnet, left_on='team', right_on='Team')
net_stats['to_display'] = '#' + net_stats['NET'].astype(str)

# For the graph title, use the list of games to find the most recent date
try:
    games = pd.read_csv(f'ncaab_stats_input_net_{season}.csv')
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
    teamlogos['logo'] = '.\\logos\\'+teamlogos['logo']
    net_stats = net_stats.merge(teamlogos, on='team')
    net_stats['to_display'] = '#' + net_stats['NET'].astype(str)
    havelogos = 1
except:
    net_stats['to_display'] = '#' + net_stats['NET'].astype(str) + ' ' + net_stats['team']
    havelogos = 0


def makeplot(title, condition):
    # Sorting them this way puts circles for the #1 team over others
    net_stats.sort_values(by='NET', ascending=False, inplace=True)
    net_stats['visibility'] = net_stats.eval(condition).astype(int)
    net_stats_subset=net_stats[net_stats['visibility']==1]
    max_x = math.ceil(net_stats['value'].max()) + 1
    max_y = 5*math.ceil(net_stats['efficiency'].max()/5)
    min_x = math.floor(net_stats_subset['value'].min())
    min_y = 5*math.floor(net_stats_subset['efficiency'].min()/5)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100, layout='constrained')
    fig.suptitle(('NET - ' + title + '\n(Games Through ' + maxdate + ')').strip())
    ax.scatter(net_stats['value'], net_stats['efficiency'], 100, net_stats['bgcolor'], alpha=0.05*(1-net_stats['visibility']))
    if havelogos == 1:
        for i in net_stats_subset.index:
            ax.annotate(net_stats_subset.at[i,'to_display'], xy=(net_stats_subset.at[i,'value'], net_stats_subset.at[i,'efficiency']), ha='center', va='bottom', xytext=(0, 12), textcoords='offset points', zorder=5000)
            ax.add_artist(AnnotationBbox(OffsetImage(plt.imread(net_stats_subset.at[i,'logo']), zoom=0.25), (net_stats_subset.at[i,'value'], net_stats_subset.at[i,'efficiency']), frameon=False))
    else:
        ax.scatter(net_stats_subset['value'], net_stats_subset['efficiency'], 100, net_stats_subset['bgcolor'], alpha=1)
        for i in net_stats_subset.index:
            ax.annotate(net_stats_subset.at[i,'to_display'], xy=(net_stats_subset.at[i,'value'], net_stats_subset.at[i,'efficiency']), ha='center', va='bottom', xytext=(0, 6), textcoords='offset points', zorder=5000)
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_ylabel('Efficiency')
    ax.set_xlabel('Value')
    ax.set_xscale('symlog')
    ax.set_xticks(np.arange(min_x, max_x, 1))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    fig.savefig(f'NET Scatter {title}.png')

makeplot("All Teams", "1==1")
makeplot("Top 25", "NET <= 25")
makeplot("Top 50", "NET <= 50")
makeplot("Top 75", "NET <= 75")
makeplot("Top 100", "NET <= 100")
makeplot("ACC", "Conference == 'ACC'")
makeplot("Big East", "Conference == 'Big East'")
makeplot("Big 12", "Conference == 'Big 12'")
makeplot("SEC", "Conference == 'SEC'")
makeplot("Big Ten", "Conference == 'Big Ten'")
makeplot("Pac-12", "Conference == 'Pac-12'")



# makeplot("ACC", 'team.isin(["Boston College","Clemson","Duke","Florida St.","Georgia Tech","Louisville","Miami (FL)","NC State","North Carolina","Notre Dame","Pittsburgh","Syracuse","Virginia","Virginia Tech","Wake Forest"])')
# makeplot("Big East", 'team.isin(["UConn","Marquette","Creighton","Xavier","Providence","Villanova","Seton Hall","St. John\'s (NY)","Butler","DePaul","Georgetown"])')
# makeplot("Big 12", 'team.isin(["Texas","Kansas","Baylor","Iowa St.","Kansas St.","West Virginia","TCU","Oklahoma St.","Texas Tech","Oklahoma","BYU","Houston","Cincinnati","UCF"])')
# makeplot("SEC", 'team.isin(["Alabama","Tennessee","Texas A&M","Arkansas","Kentucky","Auburn","Missouri","Mississippi St.","Florida","Vanderbilt","Ole Miss","LSU","Georgia","South Carolina"])')
# makeplot("Big Ten", 'team.isin(["Purdue","Indiana","Maryland","Michigan St.","Illinois","Iowa","Rutgers","Northwestern","Penn St.","Ohio St.","Michigan","Wisconsin","Nebraska","Minnesota"])')
# makeplot("Pac-12", 'team.isin(["UCLA","Arizona","Oregon","Southern California","Arizona St.","Colorado","Washington St.","Utah","Stanford","Washington","Oregon St.","California"])')
# makeplot("", 'team.isin([""])')

# temp = realnet[realnet['Conference'] == 'AAC']
# selected_column = temp['Team']
# result = '","'.join(selected_column.tolist())
# print(result)
