import pandas as pd

from utils.form_analysis import build_team_match_history


def build_league_momentum(
    matches: pd.DataFrame,
    window: int = 5
) -> pd.DataFrame:
    """
    Calculates rolling performance metrics for every team.

    Momentum is measured using points per match over the
    latest five completed matches of each team.
    """

    if window < 1:
        raise ValueError("Window must be at least 1.")

    if matches.empty:
        raise ValueError("The matches dataset is empty.")

    teams = sorted(
        set(matches["home_team"].dropna()) |
        set(matches["away_team"].dropna())
    )

    if not teams:
        raise ValueError("No teams found in the dataset.")

    team_histories = []

    for team in teams:

        history = build_team_match_history(
            matches,
            team
        )

        history = history.sort_values(
            "date",
            kind="stable"
        ).reset_index(drop=True)

        # Team identification
        history["team"] = team

        # Sequential match number for each team
        history["match_number"] = range(
            1,
            len(history) + 1
        )

        # Number of matches included in each rolling window
        history["matches_in_window"] = pd.Series(
            range(1, len(history) + 1)
        ).clip(upper=window)

        # Rolling points
        history["rolling_points"] = (
            history["points"]
            .rolling(window=window, min_periods=1)
            .sum()
            .astype(int)
        )

        # Average points per match in the rolling window
        history["rolling_points_per_match"] = (
            history["points"]
            .rolling(window=window, min_periods=1)
            .mean()
            .round(2)
        )

        # Rolling goal difference
        history["goal_difference_last_5"] = (
            history["goal_difference"]
            .rolling(window=window, min_periods=1)
            .sum()
            .astype(int)
        )

        team_histories.append(history)

    momentum = pd.concat(
        team_histories,
        ignore_index=True
    )

    return momentum[
        [
            "team",
            "date",
            "opponent",
            "venue",
            "match_number",
            "matches_in_window",
            "result",
            "points",
            "form_last_5",
            "rolling_points",
            "rolling_points_per_match",
            "goals_for_last_5",
            "goals_against_last_5",
            "goal_difference_last_5",
        ]
    ]


def build_momentum_summary(
    momentum: pd.DataFrame
) -> pd.DataFrame:
    """
    Returns the latest momentum measurements for each team.
    """

    if momentum.empty:
        raise ValueError("Momentum dataset is empty.")

    latest = (
        momentum
        .sort_values(["team", "date", "match_number"])
        .groupby("team", group_keys=False)
        .tail(1)
        .copy()
    )

    summary = latest[
        [
            "team",
            "date",
            "form_last_5",
            "matches_in_window",
            "rolling_points",
            "rolling_points_per_match",
            "goals_for_last_5",
            "goals_against_last_5",
            "goal_difference_last_5",
        ]
    ].rename(
        columns={
            "team": "Team",
            "date": "Last Match",
            "form_last_5": "Last 5 Results",
            "matches_in_window": "Matches in Window",
            "rolling_points": "Points Last 5",
            "rolling_points_per_match": "Points per Match",
            "goals_for_last_5": "Goals For",
            "goals_against_last_5": "Goals Against",
            "goal_difference_last_5": "Goal Difference",
        }
    )

    summary = summary.sort_values(
        by=[
            "Points per Match",
            "Points Last 5",
            "Goal Difference",
        ],
        ascending=False
    ).reset_index(drop=True)

    # Assign shared positions when teams have identical metrics
    ranking_keys = list(zip(
        summary["Points per Match"],
        summary["Points Last 5"],
        summary["Goal Difference"]
    ))

    summary.insert(
        0,
        "Position",
        [
            1 + sum(other > current for other in ranking_keys)
            for current in ranking_keys
        ]
    )

    return summary