
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "matches.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "clean_sheets_analysis.csv"

df = pd.read_csv(INPUT_FILE)

# Μόνο κανονική περίοδος
df = df[df["round"].str.startswith("Regular Season")].copy()

teams = sorted(set(df["home_team"]) | set(df["away_team"]))

results = []

for team in teams:

    home = df[df["home_team"] == team]
    away = df[df["away_team"] == team]

    # Clean sheets εντός έδρας
    home_clean_sheets = (home["away_goals"] == 0).sum()

    # Clean sheets εκτός έδρας
    away_clean_sheets = (away["home_goals"] == 0).sum()

    total_played = len(home) + len(away)
    total_clean_sheets = home_clean_sheets + away_clean_sheets

    results.append({
        "team": team,
        "home_played": len(home),
        "home_clean_sheets": home_clean_sheets,
        "home_clean_sheet_percentage": round(
            home_clean_sheets / len(home) * 100, 2
        ),
        "away_played": len(away),
        "away_clean_sheets": away_clean_sheets,
        "away_clean_sheet_percentage": round(
            away_clean_sheets / len(away) * 100, 2
        ),
        "total_played": total_played,
        "total_clean_sheets": total_clean_sheets,
        "total_clean_sheet_percentage": round(
            total_clean_sheets / total_played * 100, 2
        )
    })

analysis = pd.DataFrame(results)

analysis = analysis.sort_values(
    "total_clean_sheet_percentage",
    ascending=False
)

analysis.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("--- CLEAN SHEETS ANALYSIS ---")
print(analysis.to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
