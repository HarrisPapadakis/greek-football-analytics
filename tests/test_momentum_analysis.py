import pandas as pd
import pytest

from utils.momentum_analysis import (
    build_league_momentum,
    build_momentum_summary,
)


def sample_matches():

    return pd.DataFrame([
        {
            "date": "2024-08-10",
            "home_team": "AEK Athens FC",
            "away_team": "PAOK",
            "home_goals": 2,
            "away_goals": 0,
        },
        {
            "date": "2024-08-17",
            "home_team": "Olympiakos",
            "away_team": "AEK Athens FC",
            "home_goals": 1,
            "away_goals": 1,
        },
        {
            "date": "2024-08-24",
            "home_team": "AEK Athens FC",
            "away_team": "Aris",
            "home_goals": 0,
            "away_goals": 1,
        },
        {
            "date": "2024-08-31",
            "home_team": "Panathinaikos",
            "away_team": "AEK Athens FC",
            "home_goals": 1,
            "away_goals": 3,
        },
        {
            "date": "2024-09-07",
            "home_team": "AEK Athens FC",
            "away_team": "Volos NFC",
            "home_goals": 1,
            "away_goals": 2,
        },
        {
            "date": "2024-09-14",
            "home_team": "Lamia",
            "away_team": "AEK Athens FC",
            "home_goals": 2,
            "away_goals": 0,
        },
    ])


def test_momentum_last_five_matches():

    momentum = build_league_momentum(
        sample_matches()
    )

    aek = momentum[
        momentum["team"] == "AEK Athens FC"
    ].iloc[-1]

    assert aek["form_last_5"] == "D-L-W-L-L"
    assert aek["rolling_points"] == 4
    assert aek["rolling_points_per_match"] == 0.8


def test_rolling_goal_difference():

    momentum = build_league_momentum(
        sample_matches()
    )

    aek = momentum[
        momentum["team"] == "AEK Athens FC"
    ].iloc[-1]

    assert aek["goals_for_last_5"] == 5
    assert aek["goals_against_last_5"] == 7
    assert aek["goal_difference_last_5"] == -2


def test_first_match_uses_available_window():

    momentum = build_league_momentum(
        sample_matches()
    )

    aek = momentum[
        momentum["team"] == "AEK Athens FC"
    ].iloc[0]

    assert aek["matches_in_window"] == 1
    assert aek["rolling_points"] == 3
    assert aek["rolling_points_per_match"] == 3.0


def test_momentum_summary():

    momentum = build_league_momentum(
        sample_matches()
    )

    summary = build_momentum_summary(momentum)

    # Check required columns
    assert "Team" in summary.columns
    assert "Points per Match" in summary.columns
    assert "Points Last 5" in summary.columns

    # Find AEK in the summary
    aek = summary[
        summary["Team"] == "AEK Athens FC"
    ].iloc[0]

    # Verify AEK's actual momentum
    assert aek["Points per Match"] == 0.8
    assert aek["Points Last 5"] == 4
    assert aek["Last 5 Results"] == "D-L-W-L-L"

    # Verify descending ranking
    values = summary["Points per Match"].tolist()

    assert values == sorted(values, reverse=True)


def test_invalid_window():

    with pytest.raises(ValueError):
        build_league_momentum(
            sample_matches(),
            window=0
        )


def test_empty_dataset():

    with pytest.raises(ValueError):
        build_league_momentum(
            pd.DataFrame()
        )