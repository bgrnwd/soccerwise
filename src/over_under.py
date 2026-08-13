from datetime import datetime
from pathlib import Path

import polars as pl
import streamlit as st
from great_tables import GT

parent: Path = Path(__file__).parent

df: pl.DataFrame = pl.read_csv(f"{parent}/over_under.csv")
current_year: int = datetime.now().year

TABLE_COLUMNS = ["team_logo", "team_name", "points", "over_under", "doyle", "tom", "gass"]
LABELS = {
    "team_logo": "Club",
    "team_name": "",
    "gass": "Gass",
    "doyle": "Doyle",
    "tom": "Tom",
    "over_under": "Over/Under",
    "points": "Points",
}
CAPTIONS = [
    "Data is updated every Sunday, Monday, and Thursday morning. Last updated on Thursday August 13, 2026 at 09:04:09 AM UTC.",
    "The wordmarks, logos, trade names, packaging and designs of MLS, SUM, the current and former MLS member clubs are the exclusive property of MLS or their affiliates.",
    "Data courtesy of [American Soccer Analysis](https://www.americansocceranalysis.com/).",
]


def build_table(df: pl.DataFrame) -> str:
    return (
        GT(df.drop(["year", "team_id"]).select(TABLE_COLUMNS))
        .fmt_image("team_logo")
        .cols_label(LABELS)
        .data_color(columns=["over_under", "points"], palette="Greens")
        .data_color(
            columns=["tom", "gass", "doyle"],
            palette="Oranges",
            domain=["Over", "Under", "Over (Lock)", "Under (Lock)"],
        )
        .as_raw_html()
    )


st.title(body=f"{current_year} Over/Under 📈", text_alignment="center")
st.html(build_table(df))

for caption in CAPTIONS:
    st.caption(caption)
