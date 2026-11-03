
from pathlib import Path

import pandas as pd
import pytest

from utils.team_metrics import calculate_team_metrics
from utils.data_validation import validate_matches


ROOT = Path(__file__).resolve().parents[1]

MATCHES_FILE = (
    ROOT / "data" / "processed" / "matches.csv"
)


# ==================================================
# 1. SAMPLE DATA FOR TESTING
# ==================================================

@pytest.fixture
def sample_matches():

    return pd.DataFrame([

        {
            "fixture_id": 1,
            "home_team": "A",
            "away_team": "B",
            "home_goals": 2,
            "away_goals": 0
        },

        {
            "fixture_id": 2,
            "home_team": "B",
            "away_team": "A",
            "home_goals": 1,
            "away_goals": 1
        },

        {
            "fixture_id": 3,
            "home_team": "C",
            "away_team": "A",
            "home_goals": 3,
            "away_goals": 0
        }

    ])


# ==================================================
# 2. UNIT TESTS
# ==================================================

def test_team_metrics_calculation(sample_matches):

    stats = calculate_team_metrics(
        sample_matches,
        "A"
    )

    overall = stats["overall"]

    assert overall["matches_played"] == 3

    assert overall["wins"] == 1
    assert overall["draws"] == 1
    assert overall["losses"] == 1

    assert overall["points"] == 4

    assert overall["goals_scored"] == 3
    assert overall["goals_conceded"] == 4

    assert overall["goal_difference"] == -1

    assert overall["goals_per_match"] == 1.00

    assert overall["clean_sheets"] == 1

    assert overall["clean_sheet_percentage"] == 33.33


def test_home_metrics(sample_matches):

    stats = calculate_team_metrics(
        sample_matches,
        "A"
    )

    home = stats["home"]

    assert home["matches_played"] == 1
    assert home["wins"] == 1
    assert home["points"] == 3

    assert home["goals_scored"] == 2
    assert home["goals_conceded"] == 0

    assert home["clean_sheets"] == 1


def test_away_metrics(sample_matches):

    stats = calculate_team_metrics(
        sample_matches,
        "A"
    )

    away = stats["away"]

    assert away["matches_played"] == 2

    assert away["wins"] == 0
    assert away["draws"] == 1
    assert away["losses"] == 1

    assert away["points"] == 1

    assert away["goals_scored"] == 1
    assert away["goals_conceded"] == 4


def test_unknown_team_raises_error(sample_matches):

    with pytest.raises(ValueError):

        calculate_team_metrics(
            sample_matches,
            "UNKNOWN TEAM"
        )


# ==================================================
# 3. REAL DATA TESTS
# ==================================================

def test_aek_regular_season_metrics():

    df = pd.read_csv(
        MATCHES_FILE,
        encoding="utf-8-sig"
    )

    regular = df[
        df["round"].str.startswith(
            "Regular Season",
            na=False
        )
    ].dropna(
        subset=["home_goals", "away_goals"]
    ).copy()

    stats = calculate_team_metrics(
        regular,
        "AEK Athens FC"
    )

    overall = stats["overall"]

    assert overall["matches_played"] == 26

    assert overall["wins"] == 16
    assert overall["draws"] == 5
    assert overall["losses"] == 5

    assert overall["points"] == 53

    assert overall["goals_scored"] == 44
    assert overall["goals_conceded"] == 16

    assert overall["clean_sheets"] == 14


# ==================================================
# 4. DATA QUALITY TEST
# ==================================================

def test_all_data_quality_checks_pass():

    df = pd.read_csv(
        MATCHES_FILE,
        encoding="utf-8-sig"
    )

    report = validate_matches(df)

    assert not report.empty

    assert (
        report["Status"] == "PASS"
    ).all(), report.to_string(index=False)
