import re
from datetime import datetime
from pathlib import Path

import polars as pl
from itscalledsoccer.client import AmericanSoccerAnalysis

p: Path = Path(__file__)
root: Path = p.parent.parent.parent
client: AmericanSoccerAnalysis = AmericanSoccerAnalysis(lazy_load=False)
current_year: int = datetime.now().year


def update_timestamp(file: str) -> None:
    """Updates the timestamp in the given file to the current date and time."""
    with open(file, "r") as f:
        content = f.read()

    updated = datetime.now().strftime("%A %B %d, %Y at %I:%M:%S %p")
    new_content = re.sub(
        "\\w+day \\w+ \\d{2}, \\d{4} at \\d{2}:\\d{2}:\\d{2} [AP]M", updated, content
    )

    with open(file, "w+") as f:
        f.write(new_content)


def update_golden_boot():
    """Updates the standings.csv file with the latest goals, xgoals, and assists for each player."""
    standings_csv_file: str = f"{root}/src/standings.csv"
    standings_py_file: str = f"{root}/src/standings.py"
    csv_df: pl.DataFrame = pl.read_csv(standings_csv_file)
    standings_df: pl.DataFrame = pl.read_csv(standings_csv_file).filter(
        pl.col("year") == current_year
    )
    players: pl.Series = standings_df["player_id"]

    for index, player in enumerate(players.to_list()):
        if player:
            xgoal: pl.DataFrame = client.get_player_xgoals(
                player_ids=player,
                leagues="mls",
                season_name=f"{current_year}",
                stage_name="Regular Season",
            )
            standings_df[index, "goals"] = xgoal.get("goals", 0)
            standings_df[index, "xgoals"] = xgoal.get("xgoals", 0)
            standings_df[index, "assists"] = xgoal.get("primary_assists", 0)

    csv_df = csv_df.update(standings_df, left_on=["player_id", "year"], right_on=["player_id", "year"])
    csv_df.write_csv(standings_csv_file)

    update_timestamp(standings_py_file)


def update_over_under():
    """Updates the over_under.csv file with the latest points for each team."""
    over_under_csv_file: str = f"{root}/src/over_under.csv"
    over_under_py_file: str = f"{root}/src/over_under.py"
    over_under_df: pl.DataFrame = pl.read_csv(over_under_csv_file)
    teams: pl.Series = over_under_df["team_id"]

    points_list: list[int] = []

    for _, team in enumerate(teams.to_list()):
        if team:
            try:
                games_pandas = client.get_games(
                    team_ids=team,
                    leagues="mls",
                    seasons=f"{current_year}",
                    stages="Regular Season",
                )
                # Convert pandas DataFrame to Polars
                games: pl.DataFrame = pl.from_pandas(games_pandas)

                # Filter games where the team is either home or away
                team_games = games.filter(
                    (pl.col("home_team_id") == team) | (pl.col("away_team_id") == team)
                )

                # Calculate points for each game
                points_expr = (
                    pl.when(pl.col("home_team_id") == team)
                    .then(
                        pl.when(pl.col("home_score") > pl.col("away_score"))
                        .then(3)
                        .when(pl.col("home_score") == pl.col("away_score"))
                        .then(1)
                        .otherwise(0)
                    )
                    .otherwise(
                        pl.when(pl.col("away_score") > pl.col("home_score"))
                        .then(3)
                        .when(pl.col("away_score") == pl.col("home_score"))
                        .then(1)
                        .otherwise(0)
                    )
                )

                # Calculate total points
                total_points = team_games.select(points_expr.sum()).item()
                points_list.append(total_points)
            except KeyError as e:
                print(f"Error processing team {team}: {e}")
                points_list.append(0)
        else:
            points_list.append(0)

    # Add points column to dataframe
    over_under_df = over_under_df.with_columns(pl.Series("points", points_list))
    over_under_df.write_csv(over_under_csv_file)

    update_timestamp(over_under_py_file)


if __name__ == "__main__":
    update_golden_boot()
    update_over_under()
