# ncaabball

College basketball analysis with a focus on the NET, WAB, and making cool graphs.

## NET Estimates 2025

### Introduction

The NCAA Evaluation Tool (“NET”) is a computer ranking of college basketball teams. Millions of fans are interested in the NET because it's used in how teams are chosen to play for a national championship. While the exact formula is a secret, the NCAA has stated that it considers two factors: "Adjusted Net Efficiency" and "Team Value Index". I can calculate both factors and estimate the NET ranking with good accuracy.

### 





### FAQ

**Q: How is the NET calculated?**

Python code & .csv data here:\
[Code to estimate the NET](/Estimate%20NET.py) (Updated October 2024)\
[Input Data](/ncaab_stats_input_net_2025.csv)\
[Output Data](/estimated_net_output.csv)

Again, there are two components. Both are calculated with regression techniques.

The "Adjusted Net Efficiency" looks at the difference in the score per 100 possessions. (Possessions are estimated by the number of field goal attempts minus the number of offensive rebounds plus the number of turnovers plus 0.475 times the number of free throw attempts.) There is a **big** difference between winning by 50 and winning by 1. There is a **small** difference between winning by 1 and losing by 1. Winning by 6 points in 60 possessions is equal to winning by 8 points in 80 possessions.

The "Team Value Index" looks at which team won the game. This is comparable to a popular ranking method called a Bradley-Terry model. With this method, teams get a lot of credit for beating teams that beat other teams. This is not a shallow calculation of winning percentage like the RPI had. Each game affects all 364 teams.

I count the Efficiency rating at 80% and the Value rating at 20%. For example, a team that is 10th in Efficiency and 25th in Value might have a NET ranking of about 13.

**Q: Why is (whatever team) ranked so high or low?**

The NET doesn't have preseason expectations. For example, imagine that only 2 games have been played and these are the results:

* Team A beat Team B 93-51.
* Team C beat Team D 92-89.

You would probably rank these: Team A, Team C, Team D, Team B. Now see this:

* High Point beat Coppin State 93-51.
* Kansas beat UNC 92-89.

You would probably rank these: Kansas, UNC, High Point, Coppin State. The NET doesn't know that Kansas is supposed to be good, but it'll figure it out by the end of the season.

Also, due to buy games, there's a big adjustment for home court advantage in the early season. For example, imagine that these 3 games have happened:

* Team A (home) beat Team B by 28.
* Team C (home) beat Team D by 10.
* Team E (home) beat Team F by 7.

You would probably rank these: Team A, Team C, Team E, Team F, Team D, Team B.

But wait a minute. The home teams won by an average of 15 points. It's only fair to adjust for a home court advantage. Maybe this makes more sense:

* Team A is 13 points better than Team B.
* Team C is 5 points worse than Team D.
* Team E is 8 points worse than Team F.

So then they should be ranked: Team A, Team F, Team D, Team C, Team E, Team B.

This effect will be lower by March when all teams have played dozens of others in various locations.

**Q: What should my team do to have a good NET ranking?**

Win. Win by a lot. Don't lose. Don’t lose by a lot. Avoid bad field goal attempts and turnovers. I'm not saying that you can't rest your starters, but every possession counts. It's especially important to do well in non-conference games. For example, if Baylor beats Norfolk State, you can imagine that there's a transfer of credibility from Norfolk State to Baylor. And then there will be more credibility in the Big 12 and less credibility in the MEAC. But if Georgia Tech beats Syracuse and Syracuse beats Wake Forest and Wake Forest beats Georgia Tech, you can imagine that the credibility just recirculates around the ACC.

**Q: Can a team manipulate the NET by scheduling bad teams and running up the score?**

Maybe. This won't help the Value metric. For the Efficiency metric, all the teams will be compared to each other. For example, Iowa State beat Mississippi Valley State by 83-44. You probably think that's a crushing victory and it is. But the NET will also look at it like this:

* Iowa State is 52.7 points per 100 possessions better than Mississippi Valley State.
* BYU beat Mississippi Valley State by 71.0 points per 100 possessions, so Iowa State is 18.3 points per 100 possessions worse than BYU.
* Texas beat Mississippi Valley State by 71.9 points per 100 possessions, so Iowa State is 19.2 points per 100 possessions worse than Texas.
* Missouri beat Mississippi Valley State by 105.9 points per 100 possessions, so Iowa State is 53.2 points per 100 possessions worse than Missouri.

### Scatter Plots

Efficiency measures strength (teams at the top win by a lot.) Value measures record (teams at the right have quality wins.)

![Estimated NET Rankings - Top 100](/netscatter/NET%20Scatter%20Top%20100.png)

![Estimated NET Rankings - ACC](/netscatter/NET%20Scatter%20ACC.png)

More graphs are in the [netscatter](/netscatter) directory.

[Code to create plots](/Plot%20Efficiency%20Value.py)

---

## Performance Charts

![Performance of selected coaches hired in 2017-18](/performance_coachhired_selected/CoachTeamResults2018_selected.png)

[Code to make performance charts](/Performance%20Charts.py)

See more graphs for coach performance by year hired: [all coaches](/performance_coachhired_full) or [without small conferences or interim coaches](/performance_coachhired_selected).

---

## NET Estimates 2024

[Code to calculate components and estimate the NET](/NET2024/Estimate_NET_2024.py)  (Old 2023-24 version)

[Input Data](/NET2024/ncaab_stats_input_net_2024.csv)

[Output Data](/NET2024/estimated_net_output.csv)

[Actual NET rankings on Selection Sunday](/NET2024/actual_net.txt)

[Writeup](https://www.backingthepack.com/nc-state-basketball/2023/10/24/23928786/casting-a-wide-net-finding-the-basketball-rankings)

![Estimated NET Rankings - Top 100](/NET2024/NET%20Scatter%20Top%20100%202024.png)

---

## NET Estimates 2023
* [Estimate_NET_2023.py](/NET2023/Estimate_NET_2023.py): Calculating components of the NCAA Evaluation Tool ("NET") ranking. (Old 2022-23 version)
* [ncaab_stats_input_net_2023.csv](/NET2023/ncaab_stats_input_net_2023.csv): Input for the 2023 season.
* [net_estimate_output_selection_sunday_2023.csv](/NET2023/net_estimate_output_selection_sunday_2023.csv): Output, for Selection Sunday 2023.
![Top-50 NET Rankings for Selection Sunday 2023](/NET2023/NET_SS_2023_top50_logos.png)

---

## Data Sources
* The NCAA
* [sports-reference.com](https://www.sports-reference.com/cbb/)
* [Team Color Data](teamcolors.csv) (from various school websites)
* Logos are from [sportslogos.net](https://www.sportslogos.net/) and are not provided here
