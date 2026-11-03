
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "processed" / "matches.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "regular_season_table.csv"

df = pd.read_csv(INPUT_FILE)

# Κρατάμε μόνο την κανονική περίοδο
regular = df[df["round"].str.startswith("Regular Season")].copy()

teams = sorted(set(regular["home_team"]) | set(regular["away_team"]))

rows = []

for team in teams:

    home = regular[regular["home_team"] == team]
    away = regular[regular["away_team"] == team]

    played = len(home) + len(away)

    wins = (
        (home["home_goals"] > home["away_goals"]).sum()
        + (away["away_goals"] > away["home_goals"]).sum()
    )

    draws = (
        (home["home_goals"] == home["away_goals"]).sum()
        + (away["away_goals"] == away["home_goals"]).sum()
    )

    losses = played - wins - draws

    goals_for = home["home_goals"].sum() + away["away_goals"].sum()

    goals_against = home["away_goals"].sum() + away["home_goals"].sum()

    rows.append({
        "team": team,
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_difference": goals_for - goals_against,
        "points": wins * 3 + draws
    })

table = pd.DataFrame(rows)

table = table.sort_values(
    ["points", "goal_difference", "goals_for"],
    ascending=False
).reset_index(drop=True)

table.index += 1
table.index.name = "position"

table.to_csv(OUTPUT_FILE, encoding="utf-8-sig")

print("--- REGULAR SEASON TABLE ---")
print(table.to_string())

print("\nTotal matches:", len(regular))
print("Teams:", len(teams))
print("Matches per team:", sorted(table["played"].unique()))
print("Saved:", OUTPUT_FILE)
