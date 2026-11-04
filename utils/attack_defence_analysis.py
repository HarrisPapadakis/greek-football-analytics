import pandas as pd


def build_attack_defence_summary(
    matches: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculates attacking and defensive performance
    for every team in the selected competition phase.
    """

    required_columns = {
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
    }

    missing = required_columns.difference(matches.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if matches.empty:
        raise ValueError("The matches dataset is empty.")

    data = matches.copy()

    data["home_goals"] = pd.to_numeric(
        data["home_goals"], errors="coerce"
    )

    data["away_goals"] = pd.to_numeric(
        data["away_goals"], errors="coerce"
    )

    data = data.dropna(
        subset=[
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
        ]
    )

    if data.empty:
        raise ValueError("No valid completed matches found.")

    teams = sorted(
        set(data["home_team"].dropna()) |
        set(data["away_team"].dropna())
    )

    total_matches = len(data)

    total_goals = (
        data["home_goals"].sum()
        + data["away_goals"].sum()
    )

    league_average = total_goals / (2 * total_matches)

    results = []

    for team in teams:

        home = data[data["home_team"] == team]
        away = data[data["away_team"] == team]

        matches_played = len(home) + len(away)

        goals_scored = (
            home["home_goals"].sum()
            + away["away_goals"].sum()
        )

        goals_conceded = (
            home["away_goals"].sum()
            + away["home_goals"].sum()
        )

        clean_sheets = (
            home["away_goals"].eq(0).sum()
            + away["home_goals"].eq(0).sum()
        )

        failed_to_score = (
            home["home_goals"].eq(0).sum()
            + away["away_goals"].eq(0).sum()
        )

        if matches_played == 0:
            continue

        goals_per_match = goals_scored / matches_played

        goals_conceded_per_match = (
            goals_conceded / matches_played
        )

        scoring_percentage = (
            (matches_played - failed_to_score)
            / matches_played
        ) * 100

        clean_sheet_percentage = (
            clean_sheets / matches_played
        ) * 100

        results.append({
            "Team": team,
            "Matches": matches_played,
            "Goals Scored": int(goals_scored),
            "Goals Conceded": int(goals_conceded),
            "Goals per Match": round(goals_per_match, 2),
            "Goals Conceded per Match": round(
                goals_conceded_per_match, 2
            ),
            "Scoring Matches %": round(
                scoring_percentage, 2
            ),
            "Clean Sheets": int(clean_sheets),
            "Clean Sheet %": round(
                clean_sheet_percentage, 2
            ),
        })

    summary = pd.DataFrame(results)

    if summary.empty:
        raise ValueError("No team statistics could be calculated.")

    # Independent rankings:
    # Higher goals per match = better attacking output.
    # Lower goals conceded per match = better defensive output.

    summary["Attack Rank"] = (
        summary["Goals per Match"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    summary["Defence Rank"] = (
        summary["Goals Conceded per Match"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    summary["League Average"] = round(
        league_average, 2
    )

    summary = summary.sort_values(
        by=[
            "Attack Rank",
            "Defence Rank",
            "Team"
        ]
    ).reset_index(drop=True)

    return summary