# ncaabball

College basketball analysis with a focus on the NET, WAB, and making cool graphs.

## WAB Estimates 2025

### Introduction

Wins Above Bubble (“WAB”) is a measure of a college basketball team's performance. It is the number of wins that a team has minus the expected number of wins for a bubble team playing the same schedule. For example, if Clemson is 23-7 and you would expect the 45th-strongest team to be 20-10 with Clemson's schedule, Clemson's WAB would be 3.

The NCAA learned to make WAB from Bart Torvik. Every game has a value based on its difficulty. For example, a win against a good team would add 0.80 to your WAB and a loss would subtract 0.20. A win against a bubble team would add 0.50 to your WAB and a loss would subtract 0.50. A win against a bad team would add 0.01 to your WAB and a loss would subtract 0.99.

### FAQ

**Q: How is WAB calculated?**

Python code & input/output data:\
[Code to estimate WAB](/Estimate%20WAB.py)\
Input: [2025 game results](/ncaab_stats_input_2025.csv)\
Input: [2025 NET rankings on Selection Sunday](/actual_net_20250316.txt)\
Output: [2025 Estimated WAB vs. Actual WAB](/estimated_wab_output_2025.csv)\
Output: [2025 WAB impact per game](/game_impact_wab_2025.txt)

The first step is to calculate each team's offensive and defensive efficiencies. This is the number of points per 100 possessions that were scored and allowed, adjusted for the opponent's strength. An elite team may have offense=125 and defense=90. A top-30 team may have offense=120 and defense=95. A bad team may have offense=90 and defense=110. (Note: the NCAA and Bart Torvik calculate efficiency differently. The NCAA counts every game equally. Bart Torvik gives less credit to older games and to blowout wins.)

Next, use a "Pythagorean expectation" formula to turn the offense and defense into a strength value between 0 and 1.
The elite team has a strength of 125^11.5 / (125^11.5 + 90^11.5) = 0.978
The top-30 team has a strength of 120^11.5 / (120^11.5 + 95^11.5) = 0.936
The bad team has a strength of 90^11.5 / (90^11.5 + 110^11.5) = 0.090

Next, rank teams by this "pythag" strength and decide how to define the "bubble team". Average the offensive and defensive efficiencies for the 44th, 45th, and 46th strongest teams. Using this, perhaps the bubble team has offense=116 and defense=96, so its pythag strength is 116^11.5 / (116^11.5 + 96^11.5) = 0.898.

Then the NCAA assigns the team strengths in order of the NET rankings. For example, on Selection Sunday 2025, the top 3 pythag strengths were Duke (0.990), Houston (0.989), and Auburn (0.986). However, the top 3 NET rankings were #1 Duke, #2 Auburn, and #3 Houston. So #1 Duke kept its own strength of 0.990, #2 Auburn got the #2 strength (0.989, from Houston), and #3 Houston got the #3 strength (0.986, from Auburn). Bart Torvik's WAB doesn't use the NET.

Next, calculate the game's value using your opponent's strength versus the bubble team's strength. (This function is called the log5 formula and it has a long history in baseball analytics and other rating systems.)
game_wab = (opponent_pythag \* (1 - bubble_pythag)) / (opponent_pythag \* (1 - bubble_pythag) + bubble_pythag \* (1 - opponent_pythag))
Examples:
Playing against the elite team:  (0.978 \* (1 - 0.898)) / (0.978 \* (1 - 0.898) + 0.898 \* (1 - 0.978)) = 0.835
Playing against the top-30 team: (0.936 \* (1 - 0.898)) / (0.936 \* (1 - 0.898) + 0.898 \* (1 - 0.936)) = 0.624
Playing against the bad team:    (0.090 \* (1 - 0.898)) / (0.090 \* (1 - 0.898) + 0.898 \* (1 - 0.090)) = 0.011

The team earns that value for a win and loses one minus that value for a loss. For example, 0.75 for a win and -0.25 for a loss. Sum every game's value for the team's season total WAB.

A team adds 0.835 to its WAB for beating the elite team, or loses (1 - 0.835) = 0.165 for losing.
A team adds 0.624 to its WAB for beating the top-30 team, or loses (1 - 0.624) = 0.376 for losing.
A team adds 0.011 to its WAB for beating the bad team, or loses (1 - 0.011) = 0.989 for losing.

The above is correct for neutral site games. To account for home court advantage, give a 1.3% advantage to playing at home and a 1.3% disadvantage to playing away. The math looks like this:

The elite team (home) has a strength of (125\*1.013)^11.5 / ((125\*1.013)^11.5 + (90\*0.987)^11.5) = 0.983  
The elite team (away) has a strength of (125\*0.987)^11.5 / ((125\*0.987)^11.5 + (90\*1.013)^11.5) = 0.970

The top-30 team (home) has a strength of (120\*1.013)^11.5 / ((120\*1.013)^11.5 + (95\*0.987)^11.5) = 0.952
The top-30 team (away) has a strength of (120\*0.987)^11.5 / ((120\*0.987)^11.5 + (95\*1.013)^11.5) = 0.916

The bad team (home) has a strength of (90\*1.013)^11.5 / ((90\*1.013)^11.5 + (110\*0.987)^11.5) = 0.118
The bad team (away) has a strength of (90\*0.987)^11.5 / ((90\*0.987)^11.5 + (110\*1.013)^11.5) = 0.069

The hypothetical bubble team (home) has a strength of (116\*1.013)^11.5 / ((116\*1.013)^11.5 + (96\*0.987)^11.5) = 0.922
The hypothetical bubble team (away) has a strength of (116\*0.987)^11.5 / ((116\*0.987)^11.5 + (96\*1.013)^11.5) = 0.867

Reminder: do not consider the strength of the team for which you are calculating the WAB. Use the strength of the hypothetical bubble team against the opponents and adjust both for home and away.

Playing at home against the elite team:  (0.970 \* (1 - 0.922)) / (0.970 \* (1 - 0.922) + 0.922 \* (1 - 0.970)) = 0.732
Playing at home against the top-30 team: (0.916 \* (1 - 0.922)) / (0.916 \* (1 - 0.922) + 0.922 \* (1 - 0.916)) = 0.478
Playing at home against the bad team:    (0.069 \* (1 - 0.922)) / (0.069 \* (1 - 0.922) + 0.922 \* (1 - 0.069)) = 0.006

Playing on the road against the elite team:  (0.983 \* (1 - 0.867)) / (0.983 \* (1 - 0.867) + 0.867 \* (1 - 0.983)) = 0.900
Playing on the road against the top-30 team: (0.952 \* (1 - 0.867)) / (0.952 \* (1 - 0.867) + 0.867 \* (1 - 0.952)) = 0.752
Playing on the road against the bad team:    (0.118 \* (1 - 0.867)) / (0.118 \* (1 - 0.867) + 0.867 \* (1 - 0.118)) = 0.020

If you're still struggling with the concept, imagine games that a bubble team would have a 40% chance of winning. For example, a home game against the #15 team, or an away game against the #50 team, or a neutral game against the #33 team. The game values would be 0.6.
If a team plays 10 such games and goes 10-0, its WAB would be 6. (0.6 \* 10)
If a team plays 10 such games and goes 0-10, its WAB would be -4. (-0.4 \* 10)
If a team plays 10 such games and goes 4-6, its WAB would be 0. (0.6 \* 4 - 0.4 \* 6)

Finally, note that the NCAA only considers division 1 opponents. For Bart Torvik, playing non-D1 teams have basically 0 reward for winning and a -1 penalty for losing.

**Q: How accurate are these calculations?**

For 2025 Selection Sunday:
* I nailed the WAB for Houston at 10.66, for Creighton at 2.69, and for Butler at -6.40.
* All teams had an estimated WAB value to be accurate within 0.50.
* 341 of 364 were accurate within 0.25.
* The team that I overestimated the most was Coppin State (estimated -19.85, actual -20.16.)
* The top 16 teams that I underestimated the most were all 16 SEC teams, with the most being Auburn (estimated 12.57, actual 13.06.) I didn't underestimate any non-SEC teams by more than 0.15. (I think it's suspicious. Yes, I know the SEC had a good season and that's accounted for in the calculations.)

I'm only calculating the NCAA's version of the WAB. I can calculate Bart Torvik's WAB using his "Barthag" strength ratings, but I haven't tried to calculate those ratings from game data.

**Q: Is WAB a good way to measure that a team deserves to be in the NCAA Tournament?**

It's clearly doing something right. It's undeniable that the teams with the best results are at the top of the rankings. I love the idea to judge teams by their total wins vs. expected wins. Most people put too much focus on big games. For example, in 2023, Arizona State made a buzzer beating halfcourt shot to beat #7 Arizona on the road. Arizona State was one of the last teams in the tournament and wouldn't have made it without that win. Now imagine a scenario where Arizona State missed that shot, but it replaced two losses against USC & Colorado with wins. Its WAB would be better in this scenario, but it would probably miss the tournament because it didn't have a signature win. How can going 1-2 against Arizona/USC/Colorado be better than going 2-1 against those same teams? I think the humans have it wrong and the WAB has it right.

I do have some complaints. I think the WAB fluctuates too much depending on which teams are ranked 44-46 and how teams enter and exit that range. I think it's undesirable that about 50 teams have a positive value for WAB while only about 45 teams could get an at-large bid. That means there are about 5 teams that have more wins than "a bubble quality team would be expected to have", yet they don't get in the tournament. If those teams are on the wrong side of the bubble, they don't have wins "above" the bubble, do they? I think both issues could be improved by using the average strength of teams ranked 40-46 instead of 44-46. Also, why does the "pythag" formula has an exponent of 11.5 and not another number? Why is the home court adjustment a multiplicative 1.3% and not something else? The answer is just that Bart Torvik did some backtests and thought the results looked good. (Some of the details bug me, but if it works, it works.)

I also don't like how the NCAA forces the team strength to be in order of the NET rankings. On Selection Sunday 2025, Houston was the 2nd-strongest team by efficiency and #3 in the NET. And Auburn was the 3rd-strongest team by efficiency and #2 in the NET. So if a team played Houston, it got credit for playing Auburn. And if a team played Auburn, it got credit for playing Houston. Does that make sense? It seems dumb. I mean, it's probably fine, and I can understand that the NCAA wanted to make sure that beating the #1 NET team is more valuable than beating the #2 NET team, or that beating the #50 NET team is more valuable than beating the #51 NET team. But I think it makes sense how Bart Torvik creates a resume metric (WAB) from a strength metric (Barthag). When the NCAA adds the NET (which is a combination of a strength metric and a resume metric), they're double counting the results. This basically means that you get rewarded for playing low power teams with good results and you get punished for playing high power teams with bad results. For example, if you played NET #35 UC San Diego, you got credit for playing the 35th-strongest team, Arkansas. And if you played NET #133 Syracuse, you got credit for playing the 133rd-strongest team, St. Thomas (MN).

**Q: What can my team do to have a good WAB?**

It's the usual stuff. Have a decent schedule and win games. Take more risk, get more reward. As I described in the last section, it's good to play low power teams with good records, and it's bad to play talented teams with bad records. But I doubt you can predict that when you're making the schedule. Most of the time, the NET rankings closely match team strength anyway.

There are probably some opportunities to find value. Like, perhaps a home game against George Mason is worth 0.20 WAB. If you think you have a better than 80% chance of winning that game, that's positive value. Or perhaps playing Houston is worth 0.84 at home, 0.90 neutral, and 0.95 away, and you think your chances of beating Houston are 30% at home, 15% neutral, and 5% away. The expected value for that is (0.84 \* 30%) - (0.16 \* 70%) = 0.14 at home, (0.90 \* 15%) - (0.10 \* 85%) = 0.05 neutral, and (0.95 \* 5%) - (0.05 \* 95%) = 0.00 away. So your preference would be to play them at home.

It's probably bad to play teams ranked worse than #300. You get about 0.01 credit for a win and lose 0.99 credit for a loss. A team in the top 200 might be closer to 0.05 credit for a win. That may or may not be a big difference. But note that on Saturday morning before Selection Sunday 2025, when the committee was finalizing their last teams in, North Carolina had a WAB of 0.81 and West Virginia had a WAB of 0.80.


## NET Estimates 2025

### Introduction

The NCAA Evaluation Tool (“NET”) is a computer ranking of college basketball teams. Millions of fans are interested in the NET because it's used in how teams are chosen to play for a national championship. While the exact formula is a secret, the NCAA has stated that it considers two factors: "Adjusted Net Efficiency" and "Team Value Index". I can calculate both factors and estimate the NET ranking with good accuracy.

### FAQ

**Q: How is the NET calculated?**

Python code & input/output data:\
[Code to estimate NET](/Estimate%20NET.py) (Updated October 2024)\
Input: [2025 game results](/ncaab_stats_input_2025.csv)\
Output: [Estimated NET](/estimated_net_output.csv)

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
