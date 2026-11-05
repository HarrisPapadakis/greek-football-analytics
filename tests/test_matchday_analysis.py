
import pandas as pd
import pytest

from utils.matchday_analysis import (
    build_matchday_summary,
    build_team_matchday_summary,
)


def sample_matches():
    return pd.DataFrame([
        {
            "round": "Regular Season - 1",
            "home_team": "AEK",
            "away_team": "PAOK",
            "home_goals": 2,
            "away_goals": 0,
        },
        {
            "round": "Regular Season - 1",
            "home_team": "Olympiakos",
            "away_team": "AEK",
            "home_goals": 1,
            "away_goals": 1,
        },
        {
            "round": "Regular Season - 2",
            "home_team": "Aris",
            "away_team": "PAOK",
            "home_goals": 0,
            "away_goals": 1,
        },
        {
            "round": "Regular Season - 10",
            "home_team": "AEK",
            "away_team": "Aris",
            "home_goals": 3,
            "away_goals": 1,
        },
        {
            "round": "Championship Round - 1",
            "home_team": "AEK",
            "away_team": "Olympiakos",
            "home_goals": 0,
            "away_goals": 3,
        },
    ])


def test_matchday_count_and_order():
    summary = build_matchday_summary(sample_matches())

    assert len(summary) == 3
    assert summary["Matchday Number"].tolist() == [1, 2, 10]


def test_matchday_goal_and_result_metrics():
    summary = build_matchday_summary(sample_matches())

    first = summary[
        summary["Matchday Number"] == 1
    ].iloc[0]

    assert first["Matches"] == 2
    assert first["Home Wins"] == 1
    assert first["Draws"] == 1
    assert first["Away Wins"] == 0
    assert first["Home Goals"] == 3
    assert first["Away Goals"] == 1
    assert first["Total Goals"] == 4
    assert first["Goals per Match"] == 2.0


def test_second_matchday_away_win():
    summary = build_matchday_summary(sample_matches())

    second = summary[
        summary["Matchday Number"] == 2
    ].iloc[0]

    assert second["Matches"] == 1
    assert second["Away Wins"] == 1
    assert second["Total Goals"] == 1


def test_post_season_matches_are_excluded():
    summary = build_matchday_summary(sample_matches())

    assert summary["Matches"].sum() == 4
    assert summary["Matchday Number"].tolist() == [1, 2, 10]


def test_team_matchday_results():
    details = build_team_matchday_summary(sample_matches())

    aek_home = details[
        (details["Team"] == "AEK")
        & (details["matchday_number"] == 1)
        & (details["Venue"] == "Home")
    ].iloc[0]

    assert aek_home["Opponent"] == "PAOK"
    assert aek_home["Goals For"] == 2
    assert aek_home["Goals Against"] == 0
    assert aek_home["Goal Difference"] == 2
    assert aek_home["Result"] == "W"
    assert aek_home["Points"] == 3


def test_team_records_count():
    details = build_team_matchday_summary(sample_matches())

    # Four Regular Season matches × two team records per match
    assert len(details) == 8

    # AEK played two matches in Matchday 1
    aek_matchday_1 = details[
        (details["Team"] == "AEK")
        & (details["matchday_number"] == 1)
    ]

    assert len(aek_matchday_1) == 2


def test_empty_dataset():
    with pytest.raises(ValueError):
        build_matchday_summary(pd.DataFrame())


def test_missing_columns():
    with pytest.raises(ValueError):
        build_matchday_summary(
            pd.DataFrame({
                "home_team": ["AEK"]
            })
        )
