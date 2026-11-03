
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.team_metrics import calculate_team_metrics


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("⚽ Team Analysis")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Detailed team performance analysis | Regular Season"
)

st.divider()


# ==================================================
# 2. LOAD DATA
# ==================================================

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


teams = sorted(
    set(regular["home_team"].dropna()) |
    set(regular["away_team"].dropna())
)

if not teams:
    st.error("No teams found.")
    st.stop()


# ==================================================
# 3. TEAM SELECTION
# ==================================================

st.header("Select Team")

selected_team = st.selectbox(
    "Choose a team",
    teams
)


# ==================================================
# 4. CALCULATE METRICS
# ==================================================

stats = calculate_team_metrics(
    regular,
    selected_team
)

overall = stats["overall"]
home = stats["home"]
away = stats["away"]


# ==================================================
# 5. MAIN KPIs
# ==================================================

st.divider()

st.header(f"{selected_team} - Performance Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Matches Played",
    overall["matches_played"]
)

k2.metric(
    "Points",
    overall["points"]
)

k3.metric(
    "Goals Scored",
    overall["goals_scored"]
)

k4.metric(
    "Goals Conceded",
    overall["goals_conceded"]
)


# ==================================================
# 6. ADDITIONAL METRICS
# ==================================================

st.subheader("Performance Metrics")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Wins / Draws / Losses",
    f'{overall["wins"]} / '
    f'{overall["draws"]} / '
    f'{overall["losses"]}'
)

m2.metric(
    "Goal Difference",
    f'{overall["goal_difference"]:+d}'
)

m3.metric(
    "Goals per Match",
    f'{overall["goals_per_match"]:.2f}'
)

m4.metric(
    "Goals Conceded per Match",
    f'{overall["goals_conceded_per_match"]:.2f}'
)


m5, m6, m7 = st.columns(3)

m5.metric(
    "Clean Sheets",
    overall["clean_sheets"]
)

m6.metric(
    "Clean Sheet %",
    f'{overall["clean_sheet_percentage"]:.2f}%'
)

m7.metric(
    "Average Points per Match",
    f'{overall["points"] / overall["matches_played"]:.2f}'
    if overall["matches_played"] > 0 else "0.00"
)


# ==================================================
# 7. HOME VS AWAY
# ==================================================

st.divider()

st.header("Home vs Away Performance")

comparison = pd.DataFrame({

    "Metric": [
        "Matches Played",
        "Wins",
        "Draws",
        "Losses",
        "Points",
        "Goals Scored",
        "Goals Conceded",
        "Goal Difference",
        "Goals per Match",
        "Clean Sheets",
        "Clean Sheet %"
    ],

    "Home": [
        home["matches_played"],
        home["wins"],
        home["draws"],
        home["losses"],
        home["points"],
        home["goals_scored"],
        home["goals_conceded"],
        home["goal_difference"],
        home["goals_per_match"],
        home["clean_sheets"],
        home["clean_sheet_percentage"]
    ],

    "Away": [
        away["matches_played"],
        away["wins"],
        away["draws"],
        away["losses"],
        away["points"],
        away["goals_scored"],
        away["goals_conceded"],
        away["goal_difference"],
        away["goals_per_match"],
        away["clean_sheets"],
        away["clean_sheet_percentage"]
    ]

})

st.dataframe(
    comparison,
    width="stretch",
    hide_index=True
)


# ==================================================
# 8. GOALS VISUALIZATION
# ==================================================

st.divider()

st.header("Goals Performance")

goals_data = pd.DataFrame({

    "Venue": [
        "Home",
        "Home",
        "Away",
        "Away"
    ],

    "Metric": [
        "Goals Scored",
        "Goals Conceded",
        "Goals Scored",
        "Goals Conceded"
    ],

    "Goals": [
        home["goals_scored"],
        home["goals_conceded"],
        away["goals_scored"],
        away["goals_conceded"]
    ]

})

goals_chart = alt.Chart(
    goals_data
).mark_bar().encode(

    x=alt.X(
        "Goals:Q",
        title="Goals",
        scale=alt.Scale(domainMin=0)
    ),

    y=alt.Y(
        "Venue:N",
        title="Venue"
    ),

    yOffset=alt.YOffset(
        "Metric:N"
    ),

    color=alt.Color(
        "Metric:N",
        title="Metric"
    ),

    tooltip=[
        "Venue",
        "Metric",
        "Goals"
    ]

).properties(
    height=250,
    title="Goals Scored vs Conceded"
)

st.altair_chart(
    goals_chart,
    width="stretch"
)


# ==================================================
# 9. MATCH HISTORY
# ==================================================

st.divider()

st.header("Match History")

team_matches = regular[
    (regular["home_team"] == selected_team) |
    (regular["away_team"] == selected_team)
].copy()


team_matches["Venue"] = team_matches.apply(
    lambda row:
        "Home"
        if row["home_team"] == selected_team
        else "Away",
    axis=1
)


team_matches["Opponent"] = team_matches.apply(
    lambda row:
        row["away_team"]
        if row["home_team"] == selected_team
        else row["home_team"],
    axis=1
)


team_matches["Goals For"] = team_matches.apply(
    lambda row:
        row["home_goals"]
        if row["home_team"] == selected_team
        else row["away_goals"],
    axis=1
)


team_matches["Goals Against"] = team_matches.apply(
    lambda row:
        row["away_goals"]
        if row["home_team"] == selected_team
        else row["home_goals"],
    axis=1
)


def get_result(row):

    if row["Goals For"] > row["Goals Against"]:
        return "Win"

    elif row["Goals For"] == row["Goals Against"]:
        return "Draw"

    return "Loss"


team_matches["Result"] = team_matches.apply(
    get_result,
    axis=1
)


team_matches["Score"] = (
    team_matches["Goals For"].astype(int).astype(str)
    + " - "
    + team_matches["Goals Against"].astype(int).astype(str)
)


team_matches["Date"] = (
    team_matches["date"].dt.strftime("%d/%m/%Y")
)


team_matches = team_matches.sort_values(
    "date",
    ascending=False
)


history_table = team_matches[
    [
        "Date",
        "Venue",
        "Opponent",
        "Score",
        "Result",
        "round"
    ]
].rename(
    columns={
        "round": "Competition Round"
    }
)


st.dataframe(
    history_table,
    width="stretch",
    hide_index=True
)


# ==================================================
# 10. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Team Analysis"
)
