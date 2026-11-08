import runpy
from pathlib import Path

import polars as pl

update_script = runpy.run_path(
    str(Path(__file__).parents[1] / ".github" / "workflows" / "update.py")
)
player_stats_from_response = update_script["player_stats_from_response"]


def test_player_stats_from_response_reads_dataframe_row() -> None:
    response = pl.DataFrame(
        {
            "goals": [2],
            "xgoals": [1.5],
            "primary_assists": [3],
            "minutes_played": [900],
        }
    )

    assert player_stats_from_response(response) == {
        "goals": 2,
        "xgoals": 1.5,
        "assists": 3,
        "minutes_played": 900,
    }


def test_player_stats_from_empty_response_defaults_to_zero() -> None:
    response = pl.DataFrame(
        schema={
            "goals": pl.Int64,
            "xgoals": pl.Float64,
            "primary_assists": pl.Int64,
            "minutes_played": pl.Int64,
        }
    )

    assert player_stats_from_response(response) == {
        "goals": 0,
        "xgoals": 0,
        "assists": 0,
        "minutes_played": 0,
    }
