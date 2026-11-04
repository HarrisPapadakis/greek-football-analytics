import pandas as pd
import pytest

from utils.attack_defence_analysis import (
    build_attack_defence_summary,
)


def sample_matches():

    return pd.DataFrame([
        {
            "home_team": "AEK",
            "away_team": "PAOK",
            "home_goals": 2,
            "away_goals": 0,
        },
        {
            "home_team": "Olympiakos",
            "away_team": "AEK",
            "home_goals": 1,
            "away_goals": 1,
        },
        {
            "home_team": "AEK",
            "away_team": "Aris",
            "home_goals": 3,
            "away_goals": 0,
        },
        {
            "home_team": "PAOK",
            "away_team": "Olympiakos",
            "home_goals": 1,
            "away_goals": 2,
        },
    ])


def test_team_match_counts():

    summary = build_attack_defence_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Matches"] == 3
    assert aek["Goals Scored"] == 6
    assert aek["Goals Conceded"] == 1


def test_attack_metrics():

    summary = build_attack_defence_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Goals per Match"] == 2.0
    assert aek["Scoring Matches %"] == 100.0


def test_defensive_metrics():

    summary = build_attack_defence_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Clean Sheets"] == 2

    assert round(
        aek["Clean Sheet %"], 2
    ) == 66.67


def test_rankings():

    summary = build_attack_defence_summary(
        sample_matches()
    )

    assert "Attack Rank" in summary.columns
    assert "Defence Rank" in summary.columns

    assert summary["Attack Rank"].min() == 1
    assert summary["Defence Rank"].min() == 1


def test_empty_dataset():

    with pytest.raises(ValueError):
        build_attack_defence_summary(
            pd.DataFrame()
        )


def test_missing_columns():

    with pytest.raises(ValueError):
        build_attack_defence_summary(
            pd.DataFrame({
                "home_team": ["AEK"]
            })
        )