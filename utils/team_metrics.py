
import pandas as pd


# ==================================================
# 1. CALCULATE HOME OR AWAY METRICS
# ==================================================

def calculate_venue_metrics(matches, team_name, venue):

    if venue == "home":

        team_matches = matches[
            matches["home_team"] == team_name
        ]

        goals_for_column = "home_goals"
        goals_against_column = "away_goals"

    elif venue == "away":

        team_matches = matches[
            matches["away_team"] == team_name
        ]

        goals_for_column = "away_goals"
        goals_against_column = "home_goals"

    else:

        raise ValueError(
            "Venue must be 'home' or 'away'."
        )

    team_matches = team_matches.dropna(
        subset=[
            goals_for_column,
            goals_against_column
        ]
    )

    goals_for = pd.to_numeric(
        team_matches[goals_for_column],
        errors="coerce"
    )

    goals_against = pd.to_numeric(
        team_matches[goals_against_column],
        errors="coerce"
    )

    played = len(team_matches)

    # Results
    wins = int(
        (goals_for > goals_against).sum()
    )

    draws = int(
        (goals_for == goals_against).sum()
    )

    losses = int(
        (goals_for < goals_against).sum()
    )

    # Goals
    total_goals_for = int(goals_for.sum())
    total_goals_against = int(goals_against.sum())

    # Points
    points = wins * 3 + draws

    # Clean sheets
    clean_sheets = int(
        (goals_against == 0).sum()
    )

    # Goal difference
    goal_difference = (
        total_goals_for - total_goals_against
    )

    # Goals per match
    goals_per_match = (
        total_goals_for / played
        if played > 0 else 0
    )

    goals_conceded_per_match = (
        total_goals_against / played
        if played > 0 else 0
    )

    clean_sheet_percentage = (
        clean_sheets / played * 100
        if played > 0 else 0
    )

    return {

        "matches_played": played,

        "wins": wins,
        "draws": draws,
        "losses": losses,

        "points": points,

        "goals_scored": total_goals_for,
        "goals_conceded": total_goals_against,

        "goal_difference": goal_difference,

        "goals_per_match": round(
            goals_per_match, 2
        ),

        "goals_conceded_per_match": round(
            goals_conceded_per_match, 2
        ),

        "clean_sheets": clean_sheets,

        "clean_sheet_percentage": round(
            clean_sheet_percentage, 2
        )

    }


# ==================================================
# 2. CALCULATE TOTAL TEAM METRICS
# ==================================================

def calculate_team_metrics(matches, team_name):

    required_columns = [
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in matches.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    available_teams = (
        set(matches["home_team"].dropna()) |
        set(matches["away_team"].dropna())
    )

    if team_name not in available_teams:

        raise ValueError(
            f"Team '{team_name}' was not found."
        )

    # Calculate home metrics
    home = calculate_venue_metrics(
        matches,
        team_name,
        "home"
    )

    # Calculate away metrics
    away = calculate_venue_metrics(
        matches,
        team_name,
        "away"
    )

    # Combine home and away statistics
    played = (
        home["matches_played"] +
        away["matches_played"]
    )

    wins = home["wins"] + away["wins"]
    draws = home["draws"] + away["draws"]
    losses = home["losses"] + away["losses"]

    points = home["points"] + away["points"]

    goals_scored = (
        home["goals_scored"] +
        away["goals_scored"]
    )

    goals_conceded = (
        home["goals_conceded"] +
        away["goals_conceded"]
    )

    clean_sheets = (
        home["clean_sheets"] +
        away["clean_sheets"]
    )

    # Overall metrics
    overall = {

        "matches_played": played,

        "wins": wins,
        "draws": draws,
        "losses": losses,

        "points": points,

        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,

        "goal_difference": (
            goals_scored - goals_conceded
        ),

        "goals_per_match": round(
            goals_scored / played, 2
        ) if played > 0 else 0,

        "goals_conceded_per_match": round(
            goals_conceded / played, 2
        ) if played > 0 else 0,

        "clean_sheets": clean_sheets,

        "clean_sheet_percentage": round(
            clean_sheets / played * 100, 2
        ) if played > 0 else 0

    }

    return {

        "team": team_name,

        "overall": overall,

        "home": home,

        "away": away

    }
