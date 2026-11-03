
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "home_away_analysis.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "goals_per_match.csv"

df = pd.read_csv(INPUT_FILE)

# Μέσος όρος γκολ ανά αγώνα
df["home_goals_per_match"] = (
    df["home_goals"] / df["home_played"]
).round(2)

df["home_conceded_per_match"] = (
    df["home_conceded"] / df["home_played"]
).round(2)

df["away_goals_per_match"] = (
    df["away_goals"] / df["away_played"]
).round(2)

df["away_conceded_per_match"] = (
    df["away_conceded"] / df["away_played"]
).round(2)

# Συνολική επιθετική και αμυντική επίδοση
df["total_goals_per_match"] = (
    (df["home_goals"] + df["away_goals"]) /
    (df["home_played"] + df["away_played"])
).round(2)

df["total_conceded_per_match"] = (
    (df["home_conceded"] + df["away_conceded"]) /
    (df["home_played"] + df["away_played"])
).round(2)

# Ταξινόμηση με βάση τη συνολική επιθετική παραγωγή
df = df.sort_values(
    "total_goals_per_match",
    ascending=False
)

columns = [
    "team",
    "home_goals_per_match",
    "home_conceded_per_match",
    "away_goals_per_match",
    "away_conceded_per_match",
    "total_goals_per_match",
    "total_conceded_per_match"
]

result = df[columns]

result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("--- GOALS PER MATCH ANALYSIS ---")
print(result.to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
