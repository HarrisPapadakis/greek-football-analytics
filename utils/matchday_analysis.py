
import pandas as pd


def _prepare_regular_season(
    matches: pd.DataFrame
) -> pd.DataFrame:
    """
    Filters and prepares Regular Season match data.
    """

    required_columns = {
        "round",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
    }

    if matches.empty:
        raise ValueError("The matches dataset is empty.")

    missing = required_columns.difference(matches.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    data = matches.copy()

    # Keep Regular Season matches only
    data = data[
        data["round"].astype("string").str.match(
            r"^Regular Season\s*-\s*\d+$",
            na=False
        )
    ].copy()

    if data.empty:
        raise ValueError("No Regular Season matches found.")

    # Convert scores to numeric values
    data["home_goals"] = pd.to_numeric(
        data["home_goals"],
        errors="coerce"
    )

    data["away_goals"] = pd.to_numeric(
        data["away_goals"],
        errors="coerce"
    )

    # Keep completed matches with valid scores
    data = data.dropna(
        subset=[
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
        ]
    ).copy()

    if data.empty:
        raise ValueError("No valid completed matches found.")

    data["home_goals"] = data["home_goals"].astype(int)
    data["away_goals"] = data["away_goals"].astype(int)

    # Extract numeric matchday
    data["matchday_number"] = (
        data["round"]
        .str.extract(
            r"Regular Season\s*-\s*(\d+)",
            expand=False
        )
        .astype(int)
    )

    data["matchday"] = (
        "Matchday "
        + data["matchday_number"].astype(str)
    )

    return data


def build_matchday_summary(
    matches: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculates overall statistics for each Regular Season matchday.
    """

    data = _prepare_regular_season(matches)

    results = []

    for matchday, group in data.groupby(
        "matchday_number",
        sort=True
    ):

        match_count = len(group)

        home_goals = int(group["home_goals"].sum())
        away_goals = int(group["away_goals"].sum())

        total_goals = home_goals + away_goals

        home_wins = int(
            (group["home_goals"] > group["away_goals"]).sum()
        )

        draws = int(
            (group["home_goals"] == group["away_goals"]).sum()
        )

        away_wins = int(
            (group["home_goals"] < group["away_goals"]).sum()
        )

        results.append({
            "Matchday": f"Matchday {matchday}",
            "Matchday Number": int(matchday),
            "Matches": match_count,
            "Home Wins": home_wins,
            "Draws": draws,
            "Away Wins": away_wins,
            "Home Goals": home_goals,
            "Away Goals": away_goals,
            "Total Goals": total_goals,
            "Goals per Match": round(
                total_goals / match_count, 2
            ),
            "Home Win %": round(
                home_wins / match_count * 100, 2
            ),
            "Draw %": round(
                draws / match_count * 100, 2
            ),
            "Away Win %": round(
                away_wins / match_count * 100, 2
            ),
        })

    return pd.DataFrame(results).sort_values(
        "Matchday Number"
    ).reset_index(drop=True)


def build_team_matchday_summary(
    matches: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculates each team's performance in every Regular Season matchday.
    """

    data = _prepare_regular_season(matches)

    # Home team records
    home = data[
        [
            "matchday_number",
            "matchday",
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
        ]
    ].copy()

    home = home.rename(columns={
        "home_team": "Team",
        "away_team": "Opponent",
        "home_goals": "Goals For",
        "away_goals": "Goals Against",
    })

    home["Venue"] = "Home"

    # Away team records
    away = data[
        [
            "matchday_number",
            "matchday",
            "away_team",
            "home_team",
            "away_goals",
            "home_goals",
        ]
    ].copy()

    away = away.rename(columns={
        "away_team": "Team",
        "home_team": "Opponent",
        "away_goals": "Goals For",
        "home_goals": "Goals Against",
    })

    away["Venue"] = "Away"

    # Combine both datasets
    team_matches = pd.concat(
        [home, away],
        ignore_index=True
    )

    # Determine match result
    team_matches["Result"] = "D"

    team_matches.loc[
        team_matches["Goals For"] > team_matches["Goals Against"],
        "Result"
    ] = "W"

    team_matches.loc[
        team_matches["Goals For"] < team_matches["Goals Against"],
        "Result"
    ] = "L"

    # Calculate points
    team_matches["Points"] = (
        team_matches["Result"]
        .map({
            "W": 3,
            "D": 1,
            "L": 0,
        })
        .astype(int)
    )

    team_matches["Goal Difference"] = (
        team_matches["Goals For"]
        - team_matches["Goals Against"]
    )

    output_columns = [
        "matchday_number",
        "matchday",
        "Team",
        "Opponent",
        "Venue",
        "Goals For",
        "Goals Against",
        "Goal Difference",
        "Result",
        "Points",
    ]

    return team_matches[
        output_columns
    ].sort_values(
        ["matchday_number", "Team"]
    ).reset_index(drop=True)
