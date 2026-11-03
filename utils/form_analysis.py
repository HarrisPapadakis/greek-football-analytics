import pandas as pd


def build_team_match_history(
    matches: pd.DataFrame,
    team_name: str
) -> pd.DataFrame:
    """
    Creates a chronological match history for a selected team.

    Calculates:
    - Opponent and venue
    - Goals scored and conceded
    - Match result (W/D/L)
    - Points earned
    - Rolling statistics over the last 5 matches
    """

    required_columns = {
        "date",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
    }

    missing_columns = required_columns.difference(matches.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Home matches
    home = matches.loc[
        matches["home_team"] == team_name,
        ["date", "away_team", "home_goals", "away_goals"]
    ].copy()

    home = home.rename(columns={
        "away_team": "opponent",
        "home_goals": "goals_for",
        "away_goals": "goals_against",
    })

    home["venue"] = "Home"

    # Away matches
    away = matches.loc[
        matches["away_team"] == team_name,
        ["date", "home_team", "away_goals", "home_goals"]
    ].copy()

    away = away.rename(columns={
        "home_team": "opponent",
        "away_goals": "goals_for",
        "home_goals": "goals_against",
    })

    away["venue"] = "Away"

    # Combine home and away matches
    history = pd.concat(
        [home, away],
        ignore_index=True
    )

    if history.empty:
        raise ValueError(f"No matches found for team: {team_name}")

    # Clean and sort data chronologically
    history["date"] = pd.to_datetime(
        history["date"],
        errors="coerce"
    )

    history["goals_for"] = pd.to_numeric(
        history["goals_for"],
        errors="coerce"
    )

    history["goals_against"] = pd.to_numeric(
        history["goals_against"],
        errors="coerce"
    )

    history = history.dropna(
        subset=["date", "goals_for", "goals_against"]
    )

    if history.empty:
        raise ValueError(
            f"No valid match results found for team: {team_name}"
        )

    history["goals_for"] = history["goals_for"].astype(int)
    history["goals_against"] = history["goals_against"].astype(int)

    history = history.sort_values(
        "date",
        kind="stable"
    ).reset_index(drop=True)

    # Calculate goal difference
    history["goal_difference"] = (
        history["goals_for"] - history["goals_against"]
    )

    # Calculate match result
    history["result"] = "D"

    history.loc[
        history["goals_for"] > history["goals_against"],
        "result"
    ] = "W"

    history.loc[
        history["goals_for"] < history["goals_against"],
        "result"
    ] = "L"

    # Calculate points
    points_mapping = {
        "W": 3,
        "D": 1,
        "L": 0,
    }

    history["points"] = history["result"].map(
        points_mapping
    )

    # Rolling statistics over the last 5 matches
    history["points_last_5"] = (
        history["points"]
        .rolling(window=5, min_periods=1)
        .sum()
        .astype(int)
    )

    history["goals_for_last_5"] = (
        history["goals_for"]
        .rolling(window=5, min_periods=1)
        .sum()
        .astype(int)
    )

    history["goals_against_last_5"] = (
        history["goals_against"]
        .rolling(window=5, min_periods=1)
        .sum()
        .astype(int)
    )

    # Form sequence: oldest to newest within each 5-match window
    history["form_last_5"] = [
        "-".join(history["result"].iloc[max(0, i - 4):i + 1])
        for i in range(len(history))
    ]

    return history[
        [
            "date",
            "opponent",
            "venue",
            "goals_for",
            "goals_against",
            "goal_difference",
            "result",
            "points",
            "form_last_5",
            "points_last_5",
            "goals_for_last_5",
            "goals_against_last_5",
        ]
    ]