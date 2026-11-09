import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from over_under_logic import (  # noqa: I001
    correct_prediction_counts,
    mark_predictions,
)


PREDICTION_COLUMNS = ["doyle", "tom", "gass"]
INCORRECT_MARKER = "✖"


def test_predictions_score_over_and_under_against_final_totals() -> None:
    df = pl.DataFrame(
        {
            "points": [51, 49],
            "over_under": [50.5, 50.5],
            "doyle": ["Over", "Under"],
            "tom": ["Under", "Over"],
            "gass": ["Over (Lock)", "Under (Lock)"],
        }
    )

    assert correct_prediction_counts(df, PREDICTION_COLUMNS) == {
        "doyle": "2/2",
        "tom": "0/2",
        "gass": "2/2",
    }

    marked = mark_predictions(df, PREDICTION_COLUMNS, INCORRECT_MARKER)
    assert marked["doyle"].to_list() == ["Over ✅", "Under ✅"]
    assert marked["tom"].to_list() == [
        f"Under {INCORRECT_MARKER}",
        f"Over {INCORRECT_MARKER}",
    ]
    assert marked["gass"].to_list() == ["Over (Lock) ✅", "Under (Lock) ✅"]


def test_unsettled_rows_are_not_counted_or_marked() -> None:
    df = pl.DataFrame(
        {
            "points": [None],
            "over_under": [50.5],
            "doyle": ["Over"],
        },
        schema_overrides={"points": pl.Int64},
    )

    assert correct_prediction_counts(df, ["doyle"]) == {"doyle": "0/0"}
    assert mark_predictions(df, ["doyle"], INCORRECT_MARKER)["doyle"].to_list() == [
        "Over"
    ]
