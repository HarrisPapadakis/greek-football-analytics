
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT_FILE = ROOT / "data" / "processed" / "home_away_analysis.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

df = pd.read_csv(INPUT_FILE)


def create_goals_chart(df, goals_for, goals_against, title, filename):

    # Ταξινόμηση με βάση τα γκολ υπέρ
    df_sorted = df.sort_values(goals_for, ascending=True)

    teams = df_sorted["team"]
    positions = range(len(df_sorted))
    bar_height = 0.35

    fig, ax = plt.subplots(figsize=(12, 8))

    # Γκολ υπέρ
    bars_for = ax.barh(
        [p - bar_height / 2 for p in positions],
        df_sorted[goals_for],
        height=bar_height,
        label="Goals Scored"
    )

    # Γκολ κατά
    bars_against = ax.barh(
        [p + bar_height / 2 for p in positions],
        df_sorted[goals_against],
        height=bar_height,
        label="Goals Conceded"
    )

    # Εμφάνιση αριθμών στις μπάρες
    ax.bar_label(bars_for, padding=3)
    ax.bar_label(bars_against, padding=3)

    ax.set_yticks(list(positions))
    ax.set_yticklabels(teams)

    ax.set_xlabel("Goals")
    ax.set_title(title)
    ax.legend()

    ax.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.show()

    print("Saved:", OUTPUT_DIR / filename)


# Γράφημα 1: Εντός έδρας
create_goals_chart(
    df,
    "home_goals",
    "home_conceded",
    "Super League Greece 2024-25: Home Goals Scored vs Conceded",
    "home_goals_analysis.png"
)

# Γράφημα 2: Εκτός έδρας
create_goals_chart(
    df,
    "away_goals",
    "away_conceded",
    "Super League Greece 2024-25: Away Goals Scored vs Conceded",
    "away_goals_analysis.png"
)
