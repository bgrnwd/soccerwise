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

wiebe: pl.DataFrame = (
    dfs[0].drop(columns_to_drop).sort(sort_by_columns, descending=True)
)
wiebe_goals: pl.DataFrame = wiebe.select(pl.sum(goals))
wiebe_xgoals: float = wiebe.select(pl.sum(xgoals))[xgoals].round(2)
wiebe_assists: pl.DataFrame = wiebe.select(pl.sum(assists))

doyle = dfs[1].drop(columns_to_drop).sort(sort_by_columns, descending=True)
doyle_goals = doyle.select(pl.sum(goals))
doyle_xgoals = doyle.select(pl.sum(xgoals))[xgoals].round(2)
doyle_assists = doyle.select(pl.sum(assists))

gass = dfs[2].drop(columns_to_drop).sort(sort_by_columns, descending=True)
gass_goals = gass.select(pl.sum(goals))
gass_xgoals = gass.select(pl.sum(xgoals))[xgoals].round(2)
gass_assists = gass.select(pl.sum(assists))

scoops = dfs[3].drop(columns_to_drop).sort(sort_by_columns, descending=True)
scoops_goals = scoops.select(pl.sum(goals))
scoops_xgoals = scoops.select(pl.sum(xgoals))[xgoals].round(2)
scoops_assists = scoops.select(pl.sum(assists))

admin = dfs[4].drop(columns_to_drop).sort(sort_by_columns, descending=True)
admin_goals = admin.select(pl.sum(goals))
admin_xgoals = admin.select(pl.sum(xgoals))[xgoals].round(2)
admin_assists = admin.select(pl.sum(assists))


def build_standings_df(dfs: list[pl.DataFrame]) -> pl.DataFrame:
    participants = []
    goals = []
    xgoals = []
    assists = []
    for df in dfs:
        participant_name = df["team"][0]
        participants.append(participant_name)
        participant_goals = df.filter(pl.col("year") == current_year).select(
            pl.sum("goals")
        )["goals"][0]
        participant_xgoals = df.filter(pl.col("year") == current_year).select(
            pl.sum("xgoals")
        )["xgoals"][0]
        participant_assists = df.filter(pl.col("year") == current_year).select(
            pl.sum("assists")
        )["assists"][0]
        goals.append(participant_goals)
        xgoals.append(participant_xgoals)
        assists.append(participant_assists)
    return pl.DataFrame(
        {"team": participants, "goals": goals, "xG": xgoals, "assists": assists}
    )


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


standings = build_standings_df(dfs).sort([goals, xgoals_label], descending=True)
standings_html = (
    GT(standings)
    .fmt_number(columns=xgoals_label, decimals=2)
    .cols_label({"team": "Team", "goals": goals_label, "assists": assists_label})
    .data_color(columns=[goals, xgoals_label, assists], palette="Greens")
    .as_raw_html()
)

st.title(body=f"{current_year} Golden Boot 👟", text_alignment="center")

st.html(standings_html)

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns([4, 5])

with st.container():
    with col1:
        st.header("Team Wiebe")
        with st.container():
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric(label=goals_label, value=wiebe_goals)
            with metric2:
                st.metric(label=xgoals_label, value=wiebe_xgoals)
        st.html(create_team_gt(wiebe))

    with col2:
        st.header("Team Doyle")
        with st.container():
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric(label=goals_label, value=doyle_goals)
            with metric2:
                st.metric(label=xgoals_label, value=doyle_xgoals)
        st.html(create_team_gt(doyle))

    with col3:
        st.header("Team Gass")
        with st.container():
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric(label=goals_label, value=gass_goals)
            with metric2:
                st.metric(label=xgoals_label, value=gass_xgoals)
        st.html(create_team_gt(gass))

with st.container():
    with col4:
        st.header("Team Tom/Calen/Witty")
        with st.container():
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric(label=goals_label, value=scoops_goals)
            with metric2:
                st.metric(label=xgoals_label, value=scoops_xgoals)
        st.html(create_team_gt(scoops))

    with col5:
        st.header("Team Admin")
        with st.container():
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric(label=goals_label, value=admin_goals)
            with metric2:
                st.metric(label=xgoals_label, value=admin_xgoals)
        st.html(create_team_gt(admin))

st.caption(
    "Data is updated every Sunday, Monday, and Thursday morning. Last updated on Thursday February 26, 2026 at 08:13:22 AM UTC."
)
st.caption(
    "The wordmarks, logos, trade names, packaging and designs of MLS, SUM, the current and former MLS member clubs are the exclusive property of MLS or their affiliates."
)
st.caption(
    "Data courtesy of [American Soccer Analysis](https://www.americansocceranalysis.com/)."
)
