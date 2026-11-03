import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "home_away_analysis.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "home_away_points.png"

# Φόρτωση δεδομένων
df = pd.read_csv(INPUT_FILE)

# Ταξινόμηση με βάση τους συνολικούς βαθμούς
df["total_points"] = df["home_points"] + df["away_points"]
df = df.sort_values("total_points", ascending=True)

# Δημιουργία γραφήματος
fig, ax = plt.subplots(figsize=(12, 8))

positions = range(len(df))
bar_height = 0.35

ax.barh(
    [p - bar_height / 2 for p in positions],
    df["home_points"],
    height=bar_height,
    label="Home Points"
)

ax.barh(
    [p + bar_height / 2 for p in positions],
    df["away_points"],
    height=bar_height,
    label="Away Points"
)

ax.set_yticks(list(positions))
ax.set_yticklabels(df["team"])

ax.set_xlabel("Points")
ax.set_title("Super League Greece 2024-25: Home vs Away Points")
ax.legend()

ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300)
plt.show()

print("Chart saved:", OUTPUT_FILE)