from datetime import datetime
from pathlib import Path

import polars as pl
import streamlit as st
from great_tables import GT

p: Path = Path(__file__)
parent: Path = p.parent

current_year: int = datetime.now().year
df: pl.DataFrame = pl.read_csv(f"{parent}/standings.csv").filter(
    pl.col("year") == current_year
)
dfs: list[pl.DataFrame] = df.partition_by("team")

goals: str = "goals"
goals_label: str = goals.capitalize()
xgoals: str = "xgoals"
xgoals_label: str = "xG"
assists: str = "assists"
assists_label: str = assists.capitalize()
columns_to_drop: list[str] = ["player_id", "team"]
sort_by_columns: list[str] = [goals, xgoals]


def cast_stats(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        [
            pl.col(goals).cast(pl.Int32),
            pl.col(xgoals).cast(pl.Float64),
            pl.col(assists).cast(pl.Int32),
        ]
    )


def summarize_team(df: pl.DataFrame) -> dict[str, object]:
    return {
        "goals": int(df[goals].sum()),
        "xG": float(df[xgoals].sum()),
        "assists": int(df[assists].sum()),
    }


def prepare_team_data(dfs: list[pl.DataFrame]) -> tuple[dict[str, pl.DataFrame], list[str]]:
    team_map = {df["team"][0]: df for df in dfs}
    return {
        team: cast_stats(team_df.drop(columns_to_drop)).sort(sort_by_columns, descending=True)
        for team, team_df in team_map.items()
    }, list(team_map)


def build_standings_df(team_dfs: dict[str, pl.DataFrame]) -> pl.DataFrame:
    rows = [
        {"team": team, **summarize_team(team_df)}
        for team, team_df in team_dfs.items()
    ]
    return pl.DataFrame(rows).sort([goals, xgoals_label], descending=[True, True])


def create_team_gt(df: pl.DataFrame) -> str:
    return (
        GT(df.drop("year"))
        .fmt_number(columns=xgoals, decimals=2)
        .fmt_image("club_logo")
        .cols_label(
            {
                "player_name": "Player",
                "goals": goals_label,
                "xgoals": xgoals_label,
                "assists": assists_label,
                "club_logo": "Club",
            }
        )
        .data_color(columns=[goals, xgoals, assists], palette="Oranges")
        .as_raw_html()
    )


team_dfs, _ = prepare_team_data(dfs)
standings = build_standings_df(team_dfs)
team_order = standings["team"].to_list()
standings_html = (
    GT(standings)
    .fmt_number(columns=xgoals_label, decimals=2)
    .cols_label({"team": "Team", "goals": goals_label, "assists": assists_label})
    .data_color(columns=[goals, xgoals_label, assists], palette="Greens")
    .as_raw_html()
)

st.title(body=f"{current_year} Golden Boot 👟", text_alignment="center")

st.html(standings_html)

team_metrics = {team: summarize_team(df) for team, df in team_dfs.items()}


def render_team_card(team: str, df: pl.DataFrame, metrics: dict[str, object]) -> None:
    st.subheader(team)
    metric1, metric2 = st.columns(2)
    metric1.metric(label=goals_label, value=metrics[goals])
    metric2.metric(label=xgoals_label, value=round(metrics["xG"], 2))
    st.html(create_team_gt(df))


cards_per_row = 3
for i in range(0, len(team_order), cards_per_row):
    row_teams = team_order[i : i + cards_per_row]
    cols = st.columns(len(row_teams))
    for col, team in zip(cols, row_teams):
        with col:
            render_team_card(team, team_dfs[team], team_metrics[team])

st.caption(
    "Data is updated every Sunday, Monday, and Thursday morning. Last updated on Sunday August 02, 2026 at 10:01:34 AM UTC."
)
st.caption(
    "The wordmarks, logos, trade names, packaging and designs of MLS, SUM, the current and former MLS member clubs are the exclusive property of MLS or their affiliates."
)
st.caption(
    "Data courtesy of [American Soccer Analysis](https://www.americansocceranalysis.com/)."
)
