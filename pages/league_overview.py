
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches


# ==========================================
# 1. LOAD DATA
# ==========================================

st.title("⚽ League Overview")

st.subheader("Super League Greece 2024-25")

try:
    df = load_matches()

except Exception as error:
    st.exception(error)
    st.stop()


regular = df[
    df["round"].str.startswith(
        "Regular Season",
        na=False
    )
].dropna(
    subset=["home_goals", "away_goals"]
).copy()


# ==========================================
# 2. LEAGUE KPIs
# ==========================================

teams = sorted(
    set(regular["home_team"]) |
    set(regular["away_team"])
)

total_matches = len(regular)

total_goals = int(
    regular["home_goals"].sum() +
    regular["away_goals"].sum()
)

average_goals = (
    total_goals / total_matches
    if total_matches > 0 else 0
)

st.header("League Statistics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Teams", len(teams))
c2.metric("Matches", total_matches)
c3.metric("Total Goals", total_goals)
c4.metric("Goals per Match", f"{average_goals:.2f}")


# ==========================================
# 3. LEAGUE STANDINGS
# ==========================================

st.divider()

st.header("League Standings")

rows = []

for team in teams:

    home = regular[regular["home_team"] == team]
    away = regular[regular["away_team"] == team]

    wins = (
        (home["home_goals"] > home["away_goals"]).sum()
        +
        (away["away_goals"] > away["home_goals"]).sum()
    )

    draws = (
        (home["home_goals"] == home["away_goals"]).sum()
        +
        (away["away_goals"] == away["home_goals"]).sum()
    )

    losses = (
        (home["home_goals"] < home["away_goals"]).sum()
        +
        (away["away_goals"] < away["home_goals"]).sum()
    )

    gf = int(
        home["home_goals"].sum()
        +
        away["away_goals"].sum()
    )

    ga = int(
        home["away_goals"].sum()
        +
        away["home_goals"].sum()
    )

    points = int(wins * 3 + draws)

    rows.append({
        "Team": team,
        "Played": len(home) + len(away),
        "Wins": int(wins),
        "Draws": int(draws),
        "Losses": int(losses),
        "GF": gf,
        "GA": ga,
        "GD": gf - ga,
        "Points": points
    })


standings = pd.DataFrame(rows)

standings = standings.sort_values(
    ["Points", "GD", "GF"],
    ascending=[False, False, False]
).reset_index(drop=True)

standings.insert(
    0,
    "Position",
    range(1, len(standings) + 1)
)

st.dataframe(
    standings,
    width="stretch",
    hide_index=True
)


# ==========================================
# 4. TOP SCORING TEAMS
# ==========================================

st.divider()

st.header("Top Scoring Teams")

home_goals = (
    regular.groupby("home_team")["home_goals"].sum()
)

away_goals = (
    regular.groupby("away_team")["away_goals"].sum()
)

goals = (
    pd.concat([home_goals, away_goals])
    .groupby(level=0)
    .sum()
    .reset_index()
)

goals.columns = ["Team", "Goals"]

goals["Goals"] = goals["Goals"].astype(int)

goals = goals.sort_values(
    "Goals",
    ascending=False
)

chart = alt.Chart(goals).mark_bar().encode(

    x=alt.X(
        "Goals:Q",
        title="Goals Scored"
    ),

    y=alt.Y(
        "Team:N",
        sort="-x",
        title="Team"
    ),

    tooltip=["Team", "Goals"]

).properties(
    height=450
)

st.altair_chart(
    chart,
    width="stretch"
)


# ==========================================
# 5. FOOTER
# ==========================================

st.divider()

st.caption(
    "Greek Football Analytics | League Overview"
)
