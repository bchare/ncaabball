# ncaabball

College basketball analysis with a focus on the NET and making cool graphs.

## NET Estimates 2025

### Introduction

The NCAA Evaluation Tool (“NET”) is a computer ranking of college basketball teams. Millions of sports fans are interested in the NET because it influences how teams are chosen to play for a national championship. While the exact formula is a secret, the NCAA has stated that it considers two factors: "Adjusted Net Efficiency" and "Team Value Index". I can calculate both factors and estimate the NET ranking with good accuracy.

### Code & Data

[Code to calculate components and estimate the NET](/Estimate%20NET.py) (Updated October 2024)

[Output Data](/estimated_net_output.csv)

[Input Data](/ncaab_stats_input_net_2025.csv)

### Scatter Plots

Efficiency measures strength (teams at the top win by a lot.) Value measures record (teams at the right have quality wins.)

![Estimated NET Rankings - Top 100](/netscatter/NET%20Scatter%20Top%20100.png)

![Estimated NET Rankings - ACC](/netscatter/NET%20Scatter%20ACC.png)

More graphs are in the [netscatter](/netscatter) directory.

[Code to create plots](/Plot%20Efficiency%20Value.py)

### FAQ

**Q: How is the NET calculated?**

There are two regression techniques. Both use the teams and location (home/away/neutral) for inputs. One considers the score and the other doesn't. You can see Python code in the "Code & Data" section.

The "Adjusted Net Efficiency" targets the difference in the score per 100 possessions. (Possessions are estimated by the number of field goal attempts minus the number of offensive rebounds plus the number of turnovers plus 0.475 times the number of free throw attempts.) With this method, there is a huge difference between winning by 50 and winning by 1. There is a small difference between winning by 1 and losing by 1. It is adjusted for pace so that winning by 6 points in 60 possessions is equal to winning by 8 points in 80 possessions.

The "Team Value Index" targets whether a team won the game. This is comparable to a Bradley-Terry model. With this method, teams get a lot of credit for beating teams that beat other teams (that beat other teams, and so on.) Each team is assigned a win and a loss against a fictional team so that undefeated or winless teams don't have extremely high or low values.

For both factors, teams are given a rating between 0-100 based on how they compare to the average. I count the Efficiency rating at 80% and the Value rating at 20%. For example, a team with an Efficiency rating of 90 and a Value rating of 60 would have an overall rating of 84 (90*0.8 + 60*0.2). Or, a team that is 10th in Efficiency and 25th in Value might have a NET ranking of about 13 (10*0.8 + 25*0.2).

**Q: Why is (whatever team) so high or low?**

The NET doesn't have preseason expectations and it doesn't know that some teams are supposed to be better than others. If I tell you, "Team A beat Team B 93-51 and Team C beat Team D 92-89", you would rank Team A the best. But the second that you know that the first game is High Point vs. Coppin State while the second game is Kansas vs. UNC, you'd say that Team C is the best. There is also a big adjustment for home court advantage in the early season considering how many buy games there are. For example, imagine I tell you, "Team 1 wins at home by 30, Team 2 wins at home by 15, Team 3 wins at home by 10, and Team 4 wins at home by 5." These home teams won by an average of 15 points, so you may conclude that playing at home is worth 15 points, so Teams 3 & 4 are actually worse than the teams that they beat. Both of these effects will be a lot more sensible by March when all teams have played dozens of others in various locations.

**Q: What should my team do to have a good NET ranking?**

Win. Win by a lot. Don't lose. Don’t lose by a lot. If you're winning by a lot at the end of the game, don't make a bad field goal attempt or turnover. It's better to win by 10 in 70 possessions than 71 possessions. I'm not saying that you can't rest your starters or can't play your walk-ons, but every possession counts. It's especially important to do well in non-conference games. For example, if Georgia Tech beats West Georgia and loses to Cincinnati, you can imagine that there's a transfer of credibility from the Atlantic Sun to the ACC, and from the ACC to the Big 12. But if Georgia Tech beats Boston College and loses to Clemson, you can imagine that the credibility gained & lost will recirculate among the 18 teams that are all playing each other.

**Q: Can a team manipulate the NET by scheduling bad teams and running up the score?**

Maybe. This will have no benefit to the Value metric. For the Efficiency metric, all the teams will be compared to each other. For example, Iowa State beat Mississippi Valley State by 83-44. You probably think that's a crushing victory and it is. But the NET will think, Iowa State only won by 39 in 74 possessions? That means they're not as good as BYU, who beat the Delta Devils by 44 in 62 possessions. Or Texas, who won by 46 in 64 possessions. Or Missouri, who won by 72 points in 68 possessions! But at least they're way ahead of Kansas State, who stunk with an 18-point win in 66 possessions. However, Mississippi Valley State probably won't lose by the same margins in its conference games, so the high major teams will look better than the SWAC teams.

---

## Performance Charts

![Performance of selected coaches hired in 2017-18](/performance_coachhired_selected/CoachTeamResults2018_selected.png)

[Code to make performance charts](/Performance%20Charts.py)

See more graphs for coach performance by year hired: [all coaches](/performance_coachhired_full) or [without small conferences or interim coaches](/performance_coachhired_selected).

---

## NET Estimates 2024

[Code to calculate components and estimate the NET](/NET2024/Estimate_NET_2024.py)  (Old 2023-24 version)

[Output Data](/NET2024/estimated_net_output.csv)

[Input Data](/NET2024/ncaab_stats_input_net_2024.csv)

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
