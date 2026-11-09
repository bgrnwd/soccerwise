import polars as pl


def mark_predictions(
    df: pl.DataFrame, prediction_columns: list[str], incorrect_marker: str
) -> pl.DataFrame:
    decided = pl.col("points").is_not_null() & pl.col("over_under").is_not_null()
    actual_over = pl.col("points") > pl.col("over_under")

    return df.with_columns(
        pl.concat_str(
            [
                pl.col(column),
                pl.when(~decided)
                .then(pl.lit(""))
                .when(
                    (
                        pl.col(column).str.starts_with("Over")
                        == actual_over
                    ).fill_null(False)
                )
                .then(pl.lit(" ✅"))
                .otherwise(pl.lit(f" {incorrect_marker}")),
            ]
        ).alias(column)
        for column in prediction_columns
    )


def correct_prediction_counts(
    df: pl.DataFrame, prediction_columns: list[str]
) -> dict[str, str]:
    decided = pl.col("points").is_not_null() & pl.col("over_under").is_not_null()
    actual_over = pl.col("points") > pl.col("over_under")
    decided_count = df.select(decided.sum()).item() or 0

    counts = {}
    for column in prediction_columns:
        predicted_over = pl.col(column).str.starts_with("Over")
        correct = ((predicted_over == actual_over).fill_null(False)) & decided
        correct_count = df.select(correct.sum()).item() or 0
        counts[column] = f"{correct_count}/{decided_count}"

    return counts
