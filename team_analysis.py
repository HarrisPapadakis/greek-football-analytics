
import pandas as pd
from pathlib import Path

# Διαδρομές αρχείων
ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "processed" / "matches.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "team_statistics.csv"

# Φόρτωση δεδομένων
df = pd.read_csv(INPUT_FILE)

# Λίστα ομάδων
teams = sorted(set(df["home_team"]) | set(df["away_team"]))

statistics = []

for team in teams:

    # Αγώνες ως γηπεδούχος
    home = df[df["home_team"] == team]

    # Αγώνες ως φιλοξενούμενος
    away = df[df["away_team"] == team]

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

    goal_difference = goals_for - goals_against

    points = wins * 3 + draws

    statistics.append({
        "team": team,
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_difference": goal_difference,
        "points": points
    })

# Δημιουργία βαθμολογικού πίνακα
table = pd.DataFrame(statistics)

table = table.sort_values(
    by=["points", "goal_difference", "goals_for"],
    ascending=False
).reset_index(drop=True)

table.index += 1
table.index.name = "position"

# Αποθήκευση
table.to_csv(OUTPUT_FILE, encoding="utf-8-sig")

print("--- SUPER LEAGUE 1 TEAM STATISTICS ---")
print(table.to_string())

print("\nΑποθηκεύτηκε:", OUTPUT_FILE)
