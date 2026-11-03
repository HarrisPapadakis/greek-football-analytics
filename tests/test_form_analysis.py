import pandas as pd

from utils.form_analysis import build_team_match_history


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


def test_team_match_history_results():
    history = build_team_match_history(
        sample_matches(),
        "AEK Athens FC"
    )

    assert len(history) == 6
    assert history["result"].tolist() == [
        "W", "D", "L", "W", "L", "L"
    ]


def test_last_five_matches_form():
    history = build_team_match_history(
        sample_matches(),
        "AEK Athens FC"
    )

    latest = history.iloc[-1]

    assert latest["form_last_5"] == "D-L-W-L-L"
    assert latest["points_last_5"] == 4


def test_last_five_goals():
    history = build_team_match_history(
        sample_matches(),
        "AEK Athens FC"
    )

    latest = history.iloc[-1]

    assert latest["goals_for_last_5"] == 5
    assert latest["goals_against_last_5"] == 7