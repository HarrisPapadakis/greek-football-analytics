
from pathlib import Path

import pandas as pd

from utils.team_metrics import calculate_team_metrics


# ==================================================
# 1. PROJECT PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "matches.csv"

OUTPUT_FILE = (
    ROOT / "data" / "processed" /
    "data_quality_report.csv"
)


# ==================================================
# 2. VALIDATION FUNCTION
# ==================================================

def validate_matches(df):

    checks = []

    def add_check(name, passed, actual, expected):

        checks.append({

            "Check": name,
            "Status": "PASS" if passed else "FAIL",
            "Actual": str(actual),
            "Expected": str(expected)

        })

    # ----------------------------------------------
    # REQUIRED COLUMNS
    # ----------------------------------------------

    required_columns = [
        "fixture_id",
        "date",
        "round",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    add_check(
        "Required columns",
        len(missing_columns) == 0,
        missing_columns if missing_columns else "All present",
        "All required columns present"
    )

    if missing_columns:
        return pd.DataFrame(checks)

    # ----------------------------------------------
    # FIXTURE VALIDATION
    # ----------------------------------------------

    duplicate_ids = int(
        df["fixture_id"].duplicated().sum()
    )

    add_check(
        "Duplicate fixture IDs",
        duplicate_ids == 0,
        duplicate_ids,
        0
    )

    missing_scores = int(
        df[["home_goals", "away_goals"]]
        .isna()
        .any(axis=1)
        .sum()
    )

    add_check(
        "Matches with missing scores",
        missing_scores == 0,
        missing_scores,
        0
    )

    # ----------------------------------------------
    # NUMERIC VALIDATION
    # ----------------------------------------------

    home_goals = pd.to_numeric(
        df["home_goals"],
        errors="coerce"
    )

    away_goals = pd.to_numeric(
        df["away_goals"],
        errors="coerce"
    )

    negative_goals = int(
        (
            (home_goals < 0) |
            (away_goals < 0)
        ).sum()
    )

    add_check(
        "Negative goals",
        negative_goals == 0,
        negative_goals,
        0
    )

    # ----------------------------------------------
    # MATCH STATUS
    # ----------------------------------------------

    if "status" in df.columns:

        completed_statuses = [
            "FT",
            "AET",
            "PEN",
            "AWD",
            "WO"
        ]

        status = (
            df["status"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        incomplete_matches = int(
            (~status.isin(completed_statuses)).sum()
        )

        add_check(
            "Unfinished matches",
            incomplete_matches == 0,
            incomplete_matches,
            0
        )

    # ----------------------------------------------
    # REGULAR SEASON
    # ----------------------------------------------

    regular = df[
        df["round"].str.startswith(
            "Regular Season",
            na=False
        )
    ].dropna(
        subset=["home_goals", "away_goals"]
    ).copy()

    add_check(
        "Regular Season matches",
        len(regular) == 182,
        len(regular),
        182
    )

    teams = sorted(
        set(regular["home_team"].dropna()) |
        set(regular["away_team"].dropna())
    )

    add_check(
        "Number of teams",
        len(teams) == 14,
        len(teams),
        14
    )

    # ----------------------------------------------
    # MATCHES PER TEAM
    # ----------------------------------------------

    team_appearances = pd.concat([

        regular["home_team"].rename("team"),
        regular["away_team"].rename("team")

    ]).value_counts()

    wrong_match_counts = {
        team: int(count)
        for team, count in team_appearances.items()
        if count != 26
    }

    add_check(
        "Matches per team",
        len(wrong_match_counts) == 0
        and len(team_appearances) == 14,
        wrong_match_counts if wrong_match_counts else "All teams: 26",
        "14 teams with 26 matches each"
    )

    # ----------------------------------------------
    # GOALS CONSISTENCY
    # ----------------------------------------------

    total_match_goals = int(
        regular["home_goals"].sum() +
        regular["away_goals"].sum()
    )

    home_scoring = (
        regular.groupby("home_team")["home_goals"].sum()
    )

    away_scoring = (
        regular.groupby("away_team")["away_goals"].sum()
    )

    team_goals = (
        pd.concat([
            home_scoring,
            away_scoring
        ])
        .groupby(level=0)
        .sum()
    )

    total_team_goals = int(team_goals.sum())

    add_check(
        "Goals consistency",
        total_match_goals == total_team_goals,
        total_match_goals,
        total_team_goals
    )

    # ----------------------------------------------
    # POINTS AND RESULTS CONSISTENCY
    # ----------------------------------------------

    total_draws = int(
        (
            regular["home_goals"] ==
            regular["away_goals"]
        ).sum()
    )

    non_draw_matches = (
        len(regular) - total_draws
    )

    expected_total_points = (
        non_draw_matches * 3 +
        total_draws * 2
    )

    calculated_total_points = 0

    wins_total = 0
    losses_total = 0

    results_consistent = True

    for team in teams:

        stats = calculate_team_metrics(
            regular,
            team
        )["overall"]

        played = stats["matches_played"]

        wins = stats["wins"]
        draws = stats["draws"]
        losses = stats["losses"]

        if wins + draws + losses != played:
            results_consistent = False

        calculated_total_points += stats["points"]

        wins_total += wins
        losses_total += losses

    add_check(
        "Team results consistency",
        results_consistent,
        "All team records consistent"
        if results_consistent else "Inconsistent records",
        "Wins + Draws + Losses = Played"
    )

    add_check(
        "Total points consistency",
        calculated_total_points == expected_total_points,
        calculated_total_points,
        expected_total_points
    )

    add_check(
        "Wins and losses balance",
        wins_total == losses_total,
        f"Wins: {wins_total}, Losses: {losses_total}",
        "Wins = Losses"
    )

    # ----------------------------------------------
    # FINAL REPORT
    # ----------------------------------------------

    return pd.DataFrame(checks)


# ==================================================
# 3. RUN VALIDATION
# ==================================================

if __name__ == "__main__":

    print("\nLOADING DATA...")

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print("Rows loaded:", len(df))

    print("\nRUNNING DATA QUALITY CHECKS...\n")

    report = validate_matches(df)

    print("=" * 65)
    print("GREEK FOOTBALL ANALYTICS - DATA QUALITY REPORT")
    print("=" * 65)

    print(
        report.to_string(index=False)
    )

    # Save report
    report.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    passed = int(
        (report["Status"] == "PASS").sum()
    )

    failed = int(
        (report["Status"] == "FAIL").sum()
    )

    print("\n" + "=" * 65)

    print(f"PASSED CHECKS: {passed}")
    print(f"FAILED CHECKS: {failed}")

    print("\nReport saved to:")
    print(OUTPUT_FILE)

    print("=" * 65)
