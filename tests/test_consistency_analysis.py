
import pandas as pd
import pytest

from utils.consistency_analysis import (
    build_consistency_summary,
)


def sample_matches():

    return pd.DataFrame([
        {
            "date": "2024-08-10",
            "home_team": "AEK",
            "away_team": "PAOK",
            "home_goals": 2,
            "away_goals": 0,
        },
        {
            "date": "2024-08-17",
            "home_team": "Olympiakos",
            "away_team": "AEK",
            "home_goals": 1,
            "away_goals": 1,
        },
        {
            "date": "2024-08-24",
            "home_team": "AEK",
            "away_team": "Aris",
            "home_goals": 0,
            "away_goals": 1,
        },
    ])


def test_match_counts_and_points():

    summary = build_consistency_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Matches"] == 3
    assert aek["Wins"] == 1
    assert aek["Draws"] == 1
    assert aek["Losses"] == 1
    assert aek["Points"] == 4


def test_points_per_match():

    summary = build_consistency_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Points per Match"] == 1.33


def test_points_standard_deviation():

    summary = build_consistency_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Points Std Dev"] == 1.247


def test_goal_difference_standard_deviation():

    summary = build_consistency_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Goal Difference Std Dev"] == 1.247


def test_scoring_and_clean_sheet_percentages():

    summary = build_consistency_summary(
        sample_matches()
    )

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Scoring Matches %"] == 66.67
    assert aek["Clean Sheet %"] == 33.33
    assert aek["Clean Sheets"] == 1


def test_single_match_has_zero_variability():

    matches = pd.DataFrame([{
        "date": "2024-08-10",
        "home_team": "AEK",
        "away_team": "PAOK",
        "home_goals": 2,
        "away_goals": 0,
    }])

    summary = build_consistency_summary(matches)

    aek = summary[
        summary["Team"] == "AEK"
    ].iloc[0]

    assert aek["Points Std Dev"] == 0
    assert aek["Goal Difference Std Dev"] == 0


def test_empty_dataset():

    with pytest.raises(ValueError):
        build_consistency_summary(pd.DataFrame())


def test_missing_columns():

    with pytest.raises(ValueError):
        build_consistency_summary(
            pd.DataFrame({
                "home_team": ["AEK"]
            })
        )
