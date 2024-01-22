# ncaabball

College basketball analysis with a focus on the NET and making cool graphs.

## NET Estimates 2024

[Code to calculate components and estimate the NET](/Estimate%20NET.py)

[Output Data](/estimated_net_output.csv)

[Input Data](ncaab_stats_input_net_2024.csv)

[Writeup](https://www.backingthepack.com/nc-state-basketball/2023/10/24/23928786/casting-a-wide-net-finding-the-basketball-rankings)

### Scatter Plots

Efficiency measures strength (top of graph = advantage in points per possession). Value measures wins & losses (right of graph = quality wins).

![Estimated NET Rankings - Top 100](netscatter/NET%20Scatter%20Top%20100.png)

![Estimated NET Rankings - ACC](/netscatter/NET%20Scatter%20ACC.png)

More graphs are in the [netscatter](/netscatter) directory.

[Code to create plots](/Plot%20Efficiency%20Value.py)

[Actual NET rankings](/actual_net.txt)

[Team Color Data](teamcolors.csv)

Logos are from [sportslogos.net](https://www.sportslogos.net/) and are not provided here

---

## Performance Charts

![Performance of selected coaches hired in 2017-18](/performance_coachhired_selected/CoachTeamResults2018_selected.png)

[Code to make performance charts](/Performance%20Charts.py)

See more graphs for coach performance by year hired: [all coaches](/performance_coachhired_full) or [without small conferences or interim coaches](/performance_coachhired_selected).

---

## NET Estimates 2023
* [Estimate_NET_2023.py](/NET2023/Estimate_NET_2023.py): Calculating components of the NCAA Evaluation Tool ("NET") ranking.
* [ncaab_stats_input_net_2023.csv](/NET2023/ncaab_stats_input_net_2023.csv): Input for the 2023 season.
* [net_estimate_output_selection_sunday_2023.csv](/NET2023/net_estimate_output_selection_sunday_2023.csv): Output, for Selection Sunday 2023.
![Top-50 NET Rankings for Selection Sunday 2023](/NET2023/NET_SS_2023_top50_logos.png)

---

Data Sources:
* The NCAA
* [sports-reference.com](https://www.sports-reference.com/cbb/)
