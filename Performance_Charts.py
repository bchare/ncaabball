"""
Performance Charts for NCAA basketball coaches and teams.

Generates timeline-style bar charts showing season-by-season results.
Each horizontal bar represents one coach (or team), with colored segments
for each season. Text inside segments comes from the 'todisplay' column.

Chart types (set charttype below):
  - CoachTeamHireClass : coaches whose first season with a team is in a given year
  - CoachCandidates     : candidates for a specific coaching search (needs coach_targets.csv)
  - TeamBest            : top teams by total score in a date range
  - CoachBest           : top coaches by total score in a date range
  - SelectedCoach       : a hand-picked list of coaches

Inputs (CSV files in the same folder):
  - coach_performance.csv
  - team_performance.csv
  - coach_targets.csv   (only for CoachCandidates)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHART_TYPE = "TeamBest"   # see docstring above

# Year range used by all chart types
START_YEAR = 2017
END_YEAR = 2026

# CoachCandidates only (looking year is START_YEAR)
CHOOSE_TEAM = "Oregon"

# SelectedCoach: paste coachids (one per line) into the string
COACHES_STR = """
bobby-hurley-1
dana-altman-1
"""

# Filtering (applies to hire-class and some other views)
# (selected_teams is defined after data is loaded)

# BestFirst charts: BEST_PER_CHART teams/coaches per file, BEST_NUM_CHARTS files
# e.g. 25 and 3 -> charts for ranks 1-25, 26-50, 51-75
BEST_PER_CHART = 20
BEST_NUM_CHARTS = 2

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_DIR = Path(".")

def load_csv(name: str, required: bool = True) -> pd.DataFrame | None:
    path = DATA_DIR / name
    if not path.exists():
        msg = f"Missing {name}"
        if required:
            raise FileNotFoundError(msg)
        print(msg)
        return None
    return pd.read_csv(path)

coachperf = load_csv("coach_performance.csv")
teamperf = load_csv("team_performance.csv")
targets = load_csv("coach_targets.csv", required=False)

# Numeric columns that should be numbers
for col in ["season", "firstseason", "score", "isseason", "tourneyscore"]:
    if col in coachperf.columns:
        coachperf[col] = pd.to_numeric(coachperf[col], errors="coerce")

# ---------------------------------------------------------------------------
# Team selection (edit these lines as needed)
# ---------------------------------------------------------------------------
# selected_teams = coachperf['team'].drop_duplicates().to_frame()   # all teams
selected_teams = coachperf.loc[(coachperf['season'] == 2026) & (coachperf['conference'].isin(['A-10','Amer','ACC','Big 12','Big East','Big Ten','MWC','Pac-12','SEC','WCC'])), ['team']].drop_duplicates()
# selected_teams = coachperf.loc[(coachperf['season'] == 2026) & (coachperf['conference'].isin(['Amer','ACC','Big 12','Big East','Big Ten','Pac-12','SEC'])), ['team']].drop_duplicates()
# selected_teams = coachperf.loc[(coachperf['season'] == 2025) & (coachperf['conference'].isin(['Southern'])), ['team']].drop_duplicates()
# Only selected teams
# selected_teams = coachperf[coachperf['team'].isin(['NC State', 'LSU'])]['team'].drop_duplicates().to_frame()
# Only one state
# selected_teams = coachperf[coachperf['state'] == 'North Carolina']['team'].drop_duplicates().to_frame()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fill_missing_seasons(perf: pd.DataFrame, entity_col: str = "entity") -> pd.DataFrame:
    """Add blank rows for every entity-season combination so bars are continuous."""
    if perf.empty:
        return perf
    entities = perf[entity_col].unique()
    seasons = range(int(perf["season"].min()), int(perf["season"].max()) + 1)
    grid = pd.DataFrame(
        [(e, s) for e in entities for s in seasons],
        columns=[entity_col, "season"]
    )
    grid["team"] = ""
    grid["todisplay"] = ""
    grid["bgcolor"] = "#FFFFFF"
    grid["fgcolor"] = "#000000"
    grid["bordercolor"] = "#FFFFFF"
    # Preserve any extra columns that exist on the original
    combined = pd.concat([perf, grid], ignore_index=True)
    combined = combined.sort_values([entity_col, "season"])
    combined = combined.drop_duplicates(subset=[entity_col, "season"], keep="first")
    return combined

def wrap_display(text: str, bordercolor: str) -> str:
    """Wrap long non-season labels so they fit inside the bar."""
    if bordercolor != "white" or not isinstance(text, str) or not text:
        return text
    if len(text) <= 10:
        return text.replace(" ", "\n")
    return "\n".join(textwrap.wrap(text, width=10, break_long_words=False))

def prepare_common(perf: pd.DataFrame) -> pd.DataFrame:
    """Compute positions, font weight, and wrapped labels."""
    if perf.empty:
        return perf
    perf = perf.copy()
    perf["width"] = 1
    # Bar for season S occupies [S-1, S] so it sits between the year ticks
    perf["left"] = perf["season"] - 1
    perf["fontweight"] = np.where(
        perf["todisplay"].astype(str).str.contains("Champion", na=False),
        "bold", "regular"
    )
    perf["sumscore"] = perf.groupby("entity")["score"].transform("sum")
    # Last season for sorting (matches original logic)
    # Prefer max season where isseason > 2 if any exist, else max season
    has_real = (perf["isseason"] > 2).any()
    if has_real:
        last = perf.loc[perf["isseason"] > 2].groupby("entity")["season"].max()
    else:
        last = perf.groupby("entity")["season"].max()
    perf["last_season"] = perf["entity"].map(last).astype(float)
    # Subtract 1.5 if the entity has any isseason == 0 rows
    has_zero = perf.groupby("entity")["isseason"].transform(lambda x: (x == 0).any())
    perf.loc[has_zero, "last_season"] = perf.loc[has_zero, "last_season"] - 1.5
    perf["todisplay"] = [
        wrap_display(t, b) for t, b in zip(perf["todisplay"], perf["bordercolor"])
    ]
    return perf

# ---------------------------------------------------------------------------
# Chart-type preparers
# ---------------------------------------------------------------------------
def prepare_hire_class(df: pd.DataFrame, year: int, selected_teams: pd.DataFrame) -> pd.DataFrame:
    """Coaches whose first season with a team is `year`."""
    perf = df[df["firstseason"] == year].copy()
    # Keep coaches on a selected team OR with notable tournament success
    tourney_ok = (
        perf.groupby("coachid")["tourneyscore"]
        .transform(lambda x: (x > 0).sum() >= 3)
    ) | (
        perf.groupby("coachid")["tourneyscore"]
        .transform(lambda x: (x >= 0.20).sum() >= 1)
    )
    perf = perf[perf["team"].isin(selected_teams["team"]) | tourney_ok]
    # Drop interim coaches
    interims = perf.loc[perf["todisplay"].isin(["Interim", "Interim over"]), "coachid"].unique()
    perf = perf[~perf["coachid"].isin(interims)]
    perf["entity"] = perf["coach"] + "\n" + perf["team"]
    return perf

def prepare_candidates(df: pd.DataFrame, targets_df: pd.DataFrame,
                       team: str, year: int) -> tuple[pd.DataFrame, str]:
    """Candidates + actual hire for a specific search."""
    if targets_df is None:
        raise ValueError("coach_targets.csv is required for CoachCandidates")
    sub = targets_df[
        (targets_df["team"] == team) & (targets_df["lookingyear"] == year)
    ].copy()
    if sub.empty:
        raise ValueError(f"No targets found for {team} in {year}")
    source = str(sub.iloc[-1].get("source", sub.iloc[-1].get("coachid", "")))
    # Keep a few seasons around the search year
    window = df[
        (df["season"] > year - 3) & (df["isseason"] > 0)
    ].copy()
    perf = window.merge(sub.drop(columns=["team"], errors="ignore"), on="coachid", how="inner")
    # Actual hire
    actual = df[
        (df["team"] == team) & (df["season"] == year + 1) & (df["isseason"] > 0)
    ].copy()
    actual["order"] = 0
    perf = pd.concat([actual, perf], ignore_index=True)
    perf["entity"] = perf["coach"]
    perf = fill_missing_seasons(perf)
    # Preserve order (actual hire first / order=0)
    if "order" in perf.columns:
        perf["order"] = perf.groupby("entity")["order"].transform("min")
        perf = perf.sort_values(["order", "season"], ascending=[False, True])
    return perf, source

def prepare_team_best(df: pd.DataFrame, start: int, end: int,
                      rank_start: int = 1, rank_end: int = 50) -> pd.DataFrame:
    """Teams ranked by total score in the window, sliced to ranks [rank_start, rank_end]."""
    perf = df[(df["season"] >= start) & (df["season"] <= end)].copy()
    perf["entity"] = perf["team"]
    perf["bordercolor"] = "black"
    perf["isseason"] = 4
    perf["sumscore"] = perf.groupby("entity")["score"].transform("sum")
    ranking = (
        perf.groupby("entity")["sumscore"].first()
        .sort_values(ascending=False)
    )
    selected = ranking.iloc[rank_start - 1:rank_end].index
    perf = perf[perf["entity"].isin(selected)]
    # Sort so highest score appears at the top of the chart
    perf = perf.sort_values(["sumscore", "entity", "season"], ascending=[True, False, True])
    return perf

def prepare_coach_best(df: pd.DataFrame, start: int, end: int,
                       selected_teams: pd.DataFrame,
                       rank_start: int = 1, rank_end: int = 50,
                       min_seasons: int = 3) -> pd.DataFrame:
    """Coaches ranked by total score in the window, sliced to ranks [rank_start, rank_end]."""
    perf = df[
        (df["season"].between(start, end)) &
        (df["isseason"] > 0) &
        ((df["season"] - df["firstseason"]) < 99)
    ].copy()
    # Keep coaches on a selected team OR with notable tournament success
    tourney_ok = (
        perf.groupby("coachid")["tourneyscore"]
        .transform(lambda x: (x > 0).sum() >= 3)
    ) | (
        perf.groupby("coachid")["tourneyscore"]
        .transform(lambda x: (x >= 0.20).sum() >= 1)
    )
    perf = perf[perf["team"].isin(selected_teams["team"]) | tourney_ok]
    # Drop interim coaches
    interims = perf.loc[perf["todisplay"].isin(["Interim", "Interim over"]), "coachid"].unique()
    perf = perf[~perf["coachid"].isin(interims)]
    perf["entity"] = perf["coach"]
    perf["sumscore"] = perf.groupby("entity")["score"].transform("sum")
    perf["n_seasons"] = perf.groupby("entity")["isseason"].transform(lambda x: (x > 1).sum())
    perf = perf[perf["n_seasons"] >= min_seasons]
    ranking = (
        perf.groupby("entity")["sumscore"].first()
        .sort_values(ascending=False)
    )
    selected = ranking.iloc[rank_start - 1:rank_end].index
    perf = perf[perf["entity"].isin(selected)]
    perf = perf.sort_values(["sumscore", "entity", "season"], ascending=[True, False, True])
    return perf

def prepare_selected(df: pd.DataFrame, coach_ids: list[str],
                     start: int, end: int) -> pd.DataFrame:
    """Hand-picked list of coaches."""
    coachlist = pd.DataFrame({
        "coachid": coach_ids,
        "order": range(1, len(coach_ids) + 1)
    })
    perf = df[
        (df["season"].between(start, end)) &
        (df["isseason"] > 0) &
        ((df["season"] - df["firstseason"]) < 99)
    ].merge(coachlist, on="coachid", how="inner")
    # Label with coach name only (team shown above each bar)
    latest = (
        perf.sort_values("season")
        .groupby("coachid")
        .tail(1)[["coachid", "coach"]]
    )
    latest["entity"] = latest["coach"]
    perf = perf.merge(latest[["coachid", "entity"]], on="coachid", how="left")
    perf = fill_missing_seasons(perf)
    perf["order"] = perf.groupby("entity")["order"].transform("max")
    perf = perf.sort_values(["order", "season"], ascending=[False, True])
    return perf

# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_performance(perf: pd.DataFrame, chart_type: str, title: str,
                     filename: str, choose_season: int | None = None,
                     source: str = "") -> None:
    """Draw the timeline bar chart and save it."""
    if perf.empty:
        print(f"No data for {filename}")
        return
    perf = prepare_common(perf)
    # Chart-type specific sort
    if chart_type == "CoachTeamHireClass":
        perf = perf.sort_values(
            ["last_season", "sumscore", "entity", "season"],
            ascending=[True, True, False, True]
        )
    n_entities = perf["entity"].nunique()
    n_seasons = perf["season"].max() - perf["season"].min() + 1
    width = 2.1 + 0.93 * n_seasons
    height = 1.25 + 0.49 * n_entities
    fig, ax = plt.subplots(figsize=(width, height), dpi=100, layout="constrained")
    min_seas = int(perf["season"].min())
    max_seas = int(perf["season"].max())
    ax.barh(
        perf["entity"],
        perf["width"],
        left=perf["left"],
        color=perf["bgcolor"],
        edgecolor=perf["bordercolor"],
        height=0.7
    )
    # Text inside each segment
    for i, bar in enumerate(ax.patches):
        row = perf.iloc[i]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_y() + bar.get_height() / 2 - 0.04,
            row["todisplay"],
            ha="center", va="center",
            color=row["fgcolor"],
            weight=row["fontweight"],
            size=11
        )
        # Team name above the bar when the coach can change schools
        if chart_type in ("CoachCandidates", "CoachBest", "SelectedCoach") and pd.notna(row.get("team")) and row["team"]:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2 + 0.45,
                row["team"],
                ha="center", va="center", color="black", size=7
            )
        next_yr = row.get("nextyear")
        if chart_type in ("CoachCandidates", "CoachBest", "SelectedCoach") and next_yr in (
            "Fired", "Scandal", "Retired", "Resigned", "Health", "Interim"
        ):
            color = "red" if next_yr in ("Fired", "Scandal") else "black"
            ax.text(
                bar.get_x() + bar.get_width() * 0.95,
                bar.get_y() + bar.get_height() / 2,
                next_yr,
                ha="center", va="center", color=color, size=7, rotation=90,
                bbox=dict(facecolor="white", edgecolor="white", boxstyle="square,pad=0.1")
            )
    # Axes
    ax.set_xticks(range(min_seas - 1, max_seas + 1))
    ax.set_xlim(min_seas - 1, max_seas)
    ax.tick_params(axis="x", which="both", bottom=True, top=True,
                   labelbottom=True, labeltop=True)
    ax.set_ylabel("Coach" if chart_type != "TeamBest" else "Team")
    ax.set_xlabel("Year" if chart_type not in ("CoachCandidates", "CoachBest", "SelectedCoach") else " ")
    ax.margins(x=0, y=0)
    ax.set_ylim(-0.4, n_entities - 0.35)
    if choose_season is not None:
        ax.axvline(x=choose_season, color="black", linestyle="solid", linewidth=3)
    fig.suptitle(title)
    if source:
        plt.figtext(0.5, 0.005, f"Source: {source}", ha="center", fontsize=10)
    fig.savefig(filename)
    plt.close(fig)
    print(f"Saved {filename}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if CHART_TYPE == "CoachTeamHireClass":
        for year in range(START_YEAR, END_YEAR + 1):
            perf = prepare_hire_class(coachperf, year, selected_teams)
            title = f"Coaches starting in {year - 1}-{str(year % 100).zfill(2)}"
            suffix = "" if len(selected_teams) == len(coachperf["team"].drop_duplicates()) else "_selected"
            plot_performance(perf, CHART_TYPE, title,
                             f"CoachTeamResults{year}{suffix}.png")

    elif CHART_TYPE == "CoachCandidates":
        # Uses START_YEAR as the looking year
        perf, src = prepare_candidates(coachperf, targets, CHOOSE_TEAM, START_YEAR)
        title = (f"Likely Candidates for {CHOOSE_TEAM} in {START_YEAR}\n"
                 "Results before & after that coaching search")
        plot_performance(perf, CHART_TYPE, title,
                         f"CoachCandidates_{CHOOSE_TEAM}_{START_YEAR}.png",
                         choose_season=START_YEAR, source=src)

    elif CHART_TYPE == "TeamBest":
        total = BEST_PER_CHART * BEST_NUM_CHARTS
        for i in range(BEST_NUM_CHARTS):
            rank_start = i * BEST_PER_CHART + 1
            rank_end = (i + 1) * BEST_PER_CHART
            perf = prepare_team_best(teamperf, START_YEAR, END_YEAR, rank_start, rank_end)
            if perf.empty:
                break
            if BEST_NUM_CHARTS == 1:
                title = f"Best Results for {START_YEAR}-{END_YEAR}"
            else:
                title = f"Best {total} Results for {START_YEAR}-{END_YEAR} ({rank_start}-{rank_end})"
            plot_performance(
                perf, CHART_TYPE, title,
                f"TeamBest_{START_YEAR}_{END_YEAR}_{i + 1}.png"
            )

    elif CHART_TYPE == "CoachBest":
        total = BEST_PER_CHART * BEST_NUM_CHARTS
        for i in range(BEST_NUM_CHARTS):
            rank_start = i * BEST_PER_CHART + 1
            rank_end = (i + 1) * BEST_PER_CHART
            perf = prepare_coach_best(coachperf, START_YEAR, END_YEAR, selected_teams,
                                      rank_start, rank_end)
            if perf.empty:
                break
            if BEST_NUM_CHARTS == 1:
                title = f"Best Results for {START_YEAR}-{END_YEAR}"
            else:
                title = f"Best {total} Results for {START_YEAR}-{END_YEAR} ({rank_start}-{rank_end})"
            plot_performance(
                perf, CHART_TYPE, title,
                f"CoachBest_{START_YEAR}_{END_YEAR}_{i + 1}.png"
            )

    elif CHART_TYPE == "SelectedCoach":
        ids = [c.strip() for c in COACHES_STR.strip().splitlines() if c.strip()]
        perf = prepare_selected(coachperf, ids, START_YEAR, END_YEAR)
        plot_performance(perf, CHART_TYPE, "",
                         f"SelectedCoach_{START_YEAR}_{END_YEAR}.png")

    else:
        raise ValueError(f"Unknown chart type: {CHART_TYPE}")
