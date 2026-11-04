
import pandas as pd

from utils.form_analysis import build_team_match_history


def build_consistency_summary(
    matches: pd.DataFrame
) -> pd.DataFrame:
    """
    Measures team performance consistency.

    Metrics:
    - Points per Match
    - Points Standard Deviation
    - Goal Difference Standard Deviation
    - Scoring Matches Percentage
    - Clean Sheets Percentage

    Lower standard deviation means less variation.
    """

    required_columns = {
        "date",
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

    teams = sorted(
        set(matches["home_team"].dropna()) |
        set(matches["away_team"].dropna())
    )

    if not teams:
        raise ValueError("No teams found in dataset.")

    results = []

    for team in teams:

        history = build_team_match_history(
            matches,
            team
        )

        if history.empty:
            continue

        match_count = len(history)

        points = history["points"]
        goal_difference = history["goal_difference"]

        wins = int((history["result"] == "W").sum())
        draws = int((history["result"] == "D").sum())
        losses = int((history["result"] == "L").sum())

        total_points = int(points.sum())

        # Average performance
        points_per_match = points.mean()

        # Match-to-match variability
        points_std = points.std(ddof=0)

        goal_difference_std = (
            goal_difference.std(ddof=0)
        )

        # Attacking and defensive consistency indicators
        scoring_matches = int(
            (history["goals_for"] > 0).sum()
        )

        clean_sheets = int(
            (history["goals_against"] == 0).sum()
        )

        scoring_percentage = (
            scoring_matches / match_count
        ) * 100

        clean_sheet_percentage = (
            clean_sheets / match_count
        ) * 100

        results.append({
    "Team": team,
    "Matches": match_count,
    "Wins": wins,
    "Draws": draws,
    "Losses": losses,
    "Points": total_points,
    "Points per Match": round(
        points_per_match, 2
    ),
    "Points Std Dev": round(
        points_std, 3
    ),
    "Goal Difference Std Dev": round(
        goal_difference_std, 3
    ),
    "Scoring Matches %": round(
        scoring_percentage, 2
    ),
    "Clean Sheets": clean_sheets,
    "Clean Sheet %": round(
        clean_sheet_percentage, 2
    ),
})

    summary = pd.DataFrame(results)

    if summary.empty:
        raise ValueError(
            "No valid team performance data found."
        )

    # Presentation order:
    # Higher average points first.
    # Lower points variability breaks ties.

    summary = summary.sort_values(
        by=[
            "Points per Match",
            "Points Std Dev",
            "Team",
        ],
        ascending=[
            False,
            True,
            True,
        ]
    ).reset_index(drop=True)

    return summary
