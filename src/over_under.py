from datetime import datetime
from pathlib import Path

import polars as pl
import streamlit as st
from great_tables import GT, loc, style

from over_under_logic import correct_prediction_counts, mark_predictions

parent: Path = Path(__file__).parent

df: pl.DataFrame = pl.read_csv(f"{parent}/over_under.csv")
current_year: int = datetime.now().year

TABLE_COLUMNS = [
    "team_logo",
    "team_name",
    "points",
    "over_under",
    "doyle",
    "tom",
    "gass",
]
PREDICTION_COLUMNS = ["doyle", "tom", "gass"]
INCORRECT_MARKER = '<span style="color: #dc2626;">✖</span>'
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
    "Data is updated every Sunday, Monday, and Thursday morning. Last updated on Sunday November 08, 2026 at 11:27:40 PM UTC.",
    "The wordmarks, logos, trade names, packaging and designs of MLS, SUM, the current and former MLS member clubs are the exclusive property of MLS or their affiliates.",
    "Data courtesy of [American Soccer Analysis](https://www.americansocceranalysis.com/).",
]


def build_table(df: pl.DataFrame) -> str:
    marked_df = mark_predictions(df, PREDICTION_COLUMNS, INCORRECT_MARKER)
    table_df = marked_df.drop(["year", "team_id"]).select(TABLE_COLUMNS)
    return (
        GT(table_df)
        .fmt_image("team_logo")
        .cols_label(LABELS)
        .data_color(columns=["over_under", "points"], palette="Greens")
        .fmt_markdown(columns=PREDICTION_COLUMNS)
        .as_raw_html()
    )


def build_correct_predictions_table(df: pl.DataFrame) -> str:
    correct_counts = correct_prediction_counts(df, PREDICTION_COLUMNS)
    decided_count = df.select(
        (pl.col("points").is_not_null() & pl.col("over_under").is_not_null()).sum()
    ).item() or 0

    return (
        GT(pl.DataFrame([correct_counts]))
        .tab_header(title="Correct Predictions")
        .tab_source_note("Regular season results are final.")
        .cols_label({"doyle": "Doyle", "tom": "Tom", "gass": "Gass"})
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(),
        )
        .data_color(
            columns=PREDICTION_COLUMNS,
            palette="Greens",
            domain=sorted(
                correct_counts.values(),
                key=lambda count: int(count.split("/")[0]) / decided_count
                if decided_count
                else 0,
            ),
        )
        .as_raw_html()
    )


st.title(body=f"{current_year} Over/Under 📈", text_alignment="center")
table_column, predictions_column = st.columns([3, 1])
with table_column:
    st.html(build_table(df))
with predictions_column:
    st.html(build_correct_predictions_table(df))

for caption in CAPTIONS:
    st.caption(caption)
