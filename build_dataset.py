
import json
import pandas as pd
from pathlib import Path

# Βασικοί φάκελοι
ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw" / "fixtures_single"
PROCESSED_DIR = ROOT / "data" / "processed"

# Δημιουργία φακέλου processed αν δεν υπάρχει
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

matches = []

# Διαβάζουμε όλα τα JSON αρχεία
for file_path in RAW_DIR.glob("*.json"):

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    response = data.get("response", [])

    if not response:
        continue

    match = response[0]

    fixture = match["fixture"]
    league = match["league"]
    teams = match["teams"]
    goals = match["goals"]

    # Δημιουργία εγγραφής αγώνα
    row = {
        "fixture_id": fixture["id"],
        "date": fixture["date"],
        "referee": fixture["referee"],
        "venue": fixture["venue"]["name"],
        "city": fixture["venue"]["city"],
        "league": league["name"],
        "season": league["season"],
        "round": league["round"],
        "home_team": teams["home"]["name"],
        "away_team": teams["away"]["name"],
        "home_goals": goals["home"],
        "away_goals": goals["away"],
        "status": fixture["status"]["short"]
    }

    matches.append(row)

# Μετατροπή σε DataFrame
df = pd.DataFrame(matches)

# Μετατροπή ημερομηνίας
df["date"] = pd.to_datetime(df["date"], utc=True)

# Ταξινόμηση αγώνων
df = df.sort_values("date")

# Αποθήκευση CSV
output_file = PROCESSED_DIR / "matches.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("--- DATASET CREATED ---")
print("Total matches:", len(df))
print("Unique fixture IDs:", df["fixture_id"].nunique())
print("Output:", output_file)

print("\n--- FIRST 5 MATCHES ---")
print(df.head().to_string(index=False))

print("\n--- DATASET INFO ---")
print(df.info())
