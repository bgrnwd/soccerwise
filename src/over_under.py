from datetime import datetime
from pathlib import Path

import polars as pl
import streamlit as st
from great_tables import GT

parent: Path = Path(__file__).parent

df: pl.DataFrame = pl.read_csv(f"{parent}/over_under.csv")
current_year: int = datetime.now().year

st.title(body=f"{current_year} Over/Under 📈", text_alignment="center")

st.html(
    GT(
        df.drop(["year", "team_id"]).select(
            ["team_logo", "team_name", "points", "over_under", "doyle", "tom", "gass"]
        )
    )
    .fmt_image("team_logo")
    .cols_label(
        {
            "team_logo": "Club",
            "team_name": "",
            "gass": "Gass",
            "doyle": "Doyle",
            "tom": "Tom",
            "over_under": "Over/Under",
            "points": "Points",
        }
    )
    .data_color(columns=["over_under", "points"], palette="Greens")
    .data_color(
        columns=["tom", "gass", "doyle"],
        palette="Oranges",
        domain=["Over", "Under", "Over (Lock)", "Under (Lock)"],
    )
    .as_raw_html()
)

st.caption(
    "Data is updated every Sunday, Monday, and Thursday morning. Last updated on Monday February 23, 2026 at 08:10:05 AM UTC."
)
st.caption(
    "The wordmarks, logos, trade names, packaging and designs of MLS, SUM, the current and former MLS member clubs are the exclusive property of MLS or their affiliates."
)
st.caption(
    "Data courtesy of [American Soccer Analysis](https://www.americansocceranalysis.com/)."
)
