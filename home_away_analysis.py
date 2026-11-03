
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "matches.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "home_away_analysis.csv"

df = pd.read_csv(INPUT_FILE)

# Μόνο κανονική περίοδος
df = df[df["round"].str.startswith("Regular Season")].copy()

teams = sorted(set(df["home_team"]) | set(df["away_team"]))

results = []

for team in teams:

    home = df[df["home_team"] == team]
    away = df[df["away_team"] == team]

    # Home statistics
    home_wins = (home["home_goals"] > home["away_goals"]).sum()
    home_draws = (home["home_goals"] == home["away_goals"]).sum()
    home_losses = (home["home_goals"] < home["away_goals"]).sum()

    home_goals = home["home_goals"].sum()
    home_conceded = home["away_goals"].sum()

    home_points = home_wins * 3 + home_draws

    # Away statistics
    away_wins = (away["away_goals"] > away["home_goals"]).sum()
    away_draws = (away["away_goals"] == away["home_goals"]).sum()
    away_losses = (away["away_goals"] < away["home_goals"]).sum()

    away_goals = away["away_goals"].sum()
    away_conceded = away["home_goals"].sum()

    away_points = away_wins * 3 + away_draws

    results.append({
        "team": team,
        "home_played": len(home),
        "home_wins": home_wins,
        "home_draws": home_draws,
        "home_losses": home_losses,
        "home_goals": home_goals,
        "home_conceded": home_conceded,
        "home_points": home_points,
        "home_win_rate": round(home_wins / len(home) * 100, 2),

        "away_played": len(away),
        "away_wins": away_wins,
        "away_draws": away_draws,
        "away_losses": away_losses,
        "away_goals": away_goals,
        "away_conceded": away_conceded,
        "away_points": away_points,
        "away_win_rate": round(away_wins / len(away) * 100, 2)
    })

analysis = pd.DataFrame(results)

analysis = analysis.sort_values(
    "home_points",
    ascending=False
)

analysis.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("--- HOME VS AWAY ANALYSIS ---")
print(analysis.to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
