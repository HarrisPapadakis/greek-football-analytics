
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "clean_sheets_analysis.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "clean_sheets_chart.png"

df = pd.read_csv(INPUT_FILE)

# Ταξινόμηση βάσει συνολικού ποσοστού Clean Sheets
df = df.sort_values(
    "total_clean_sheet_percentage",
    ascending=True
)

positions = range(len(df))
bar_height = 0.35

fig, ax = plt.subplots(figsize=(12, 8))

home_bars = ax.barh(
    [p - bar_height / 2 for p in positions],
    df["home_clean_sheet_percentage"],
    height=bar_height,
    label="Home Clean Sheets %"
)

away_bars = ax.barh(
    [p + bar_height / 2 for p in positions],
    df["away_clean_sheet_percentage"],
    height=bar_height,
    label="Away Clean Sheets %"
)

ax.bar_label(home_bars, fmt="%.1f%%", padding=3)
ax.bar_label(away_bars, fmt="%.1f%%", padding=3)

ax.set_yticks(list(positions))
ax.set_yticklabels(df["team"])

ax.set_xlabel("Clean Sheet Percentage (%)")
ax.set_title("Super League Greece 2024-25: Home vs Away Clean Sheets")

ax.legend()
ax.grid(axis="x", linestyle="--", alpha=0.4)

ax.set_xlim(0, 75)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.show()

print("Chart saved:", OUTPUT_FILE)
