
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.matchday_analysis import (
    build_matchday_summary,
    build_team_matchday_summary,
)


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("📅 Matchday Analysis")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Matchday statistics, scoring trends and team performance "
    "| Regular Season"
)

st.divider()


# ==================================================
# 2. LOAD DATA
# ==================================================

try:
    df = load_matches()

    matchday_summary = build_matchday_summary(df)

    team_matchday = build_team_matchday_summary(df)

except Exception as error:
    st.exception(error)
    st.stop()


if matchday_summary.empty:
    st.warning("No matchday data available.")
    st.stop()


# ==================================================
# 3. LEAGUE OVERVIEW KPIs
# ==================================================

st.header("League Matchday Overview")

total_matchdays = len(matchday_summary)

total_matches = int(matchday_summary["Matches"].sum())

total_goals = int(matchday_summary["Total Goals"].sum())

average_goals = (
    total_goals / total_matches
    if total_matches > 0 else 0
)

highest_scoring_matchday = matchday_summary.loc[
    matchday_summary["Goals per Match"].idxmax()
]

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Matchdays",
    total_matchdays
)

k2.metric(
    "Matches Analysed",
    total_matches
)

k3.metric(
    "Total Goals",
    total_goals
)

k4.metric(
    "Goals per Match",
    f"{average_goals:.2f}"
)

st.caption(
    f'Highest scoring matchday: '
    f'{highest_scoring_matchday["Matchday"]} '
    f'({highest_scoring_matchday["Goals per Match"]:.2f} goals per match)'
)


# ==================================================
# 4. GOALS PER MATCHDAY
# ==================================================

st.divider()

st.header("Goals per Matchday")

st.caption(
    "Track how the number of goals changed throughout "
    "the Regular Season."
)

goals_chart = alt.Chart(
    matchday_summary
).mark_line(
    point=True,
    strokeWidth=2
).encode(

    x=alt.X(
        "Matchday Number:O",
        title="Matchday",
        sort="ascending"
    ),

    y=alt.Y(
        "Goals per Match:Q",
        title="Average Goals per Match",
        scale=alt.Scale(domainMin=0)
    ),

    tooltip=[
        "Matchday",
        "Matches",
        "Total Goals",
        alt.Tooltip(
            "Goals per Match:Q",
            format=".2f"
        )
    ]

).properties(
    height=350,
    title="Average Goals per Matchday"
).interactive()

st.altair_chart(
    goals_chart,
    width="stretch"
)


# ==================================================
# 5. HOME VS AWAY RESULTS
# ==================================================

st.divider()

st.header("Home vs Away Results")

st.caption(
    "Distribution of home wins, draws and away wins "
    "across the 26 Regular Season matchdays."
)

results_data = matchday_summary.melt(
    id_vars=[
        "Matchday",
        "Matchday Number"
    ],
    value_vars=[
        "Home Wins",
        "Draws",
        "Away Wins"
    ],
    var_name="Result",
    value_name="Result Count"
)

results_chart = alt.Chart(
    results_data
).mark_bar().encode(

    x=alt.X(
        "Matchday Number:O",
        title="Matchday",
        sort="ascending"
    ),

    y=alt.Y(
        "Result Count:Q",
        title="Number of Matches",
        stack="zero"
    ),

    color=alt.Color(
        "Result:N",
        title="Match Result"
    ),

    tooltip=[
        "Matchday",
        "Result",
        "Result Count"
    ]

).properties(
    height=350,
    title="Home Wins vs Draws vs Away Wins"
).interactive()

st.altair_chart(
    results_chart,
    width="stretch"
)


# ==================================================
# 6. TEAM PERFORMANCE BY MATCHDAY
# ==================================================

st.divider()

st.header("Team Performance by Matchday")

st.caption(
    "Compare the points collected by selected teams "
    "during each Regular Season matchday."
)

available_teams = sorted(
    team_matchday["Team"].unique().tolist()
)

default_teams = [
    team for team in [
        "AEK Athens FC",
        "Olympiakos Piraeus",
        "PAOK",
        "Panathinaikos"
    ]
    if team in available_teams
]

selected_teams = st.multiselect(
    "Select teams",
    options=available_teams,
    default=default_teams
)

if selected_teams:

    team_chart_data = team_matchday[
        team_matchday["Team"].isin(selected_teams)
    ].copy()

    team_chart = alt.Chart(
        team_chart_data
    ).mark_line(
        point=True,
        strokeWidth=2
    ).encode(

        x=alt.X(
            "matchday_number:O",
            title="Matchday",
            sort="ascending"
        ),

        y=alt.Y(
            "Points:Q",
            title="Points Collected",
            scale=alt.Scale(domain=[0, 3])
        ),

        color=alt.Color(
            "Team:N",
            title="Team"
        ),

        tooltip=[
            "Team",
            "matchday",
            "Opponent",
            "Venue",
            "Result",
            "Points"
        ]

    ).properties(
        height=400,
        title="Team Points by Matchday"
    ).interactive()

    st.altair_chart(
        team_chart,
        width="stretch"
    )

else:
    st.info("Select at least one team to display the chart.")


# ==================================================
# 7. MATCHDAY EXPLORER
# ==================================================

st.divider()

st.header("Matchday Explorer")

selected_matchday = st.selectbox(
    "Select Matchday",
    options=matchday_summary["Matchday Number"].tolist(),
    format_func=lambda number: f"Matchday {number}"
)

selected_summary = matchday_summary[
    matchday_summary["Matchday Number"] == selected_matchday
].iloc[0]


# Matchday KPIs
st.subheader(f"Matchday {selected_matchday} Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Matches",
    int(selected_summary["Matches"])
)

m2.metric(
    "Total Goals",
    int(selected_summary["Total Goals"])
)

m3.metric(
    "Home Wins",
    int(selected_summary["Home Wins"])
)

m4.metric(
    "Away Wins",
    int(selected_summary["Away Wins"])
)


# Matchday fixtures
regular_fixtures = df[
    df["round"] == f"Regular Season - {selected_matchday}"
].dropna(
    subset=["home_goals", "away_goals"]
).copy()

st.subheader("Matchday Fixtures and Results")

regular_fixtures["Score"] = (
    regular_fixtures["home_goals"].astype(int).astype(str)
    + " - "
    + regular_fixtures["away_goals"].astype(int).astype(str)
)

fixtures_table = regular_fixtures[
    [
        "home_team",
        "away_team",
        "Score",
        "date"
    ]
].rename(
    columns={
        "home_team": "Home Team",
        "away_team": "Away Team",
        "date": "Date"
    }
)

st.dataframe(
    fixtures_table,
    width="stretch",
    hide_index=True
)


# Team performance in selected matchday
st.subheader("Team Performance")

selected_team_performance = team_matchday[
    team_matchday["matchday_number"] == selected_matchday
].copy()

st.dataframe(
    selected_team_performance[
        [
            "Team",
            "Opponent",
            "Venue",
            "Goals For",
            "Goals Against",
            "Goal Difference",
            "Result",
            "Points"
        ]
    ],
    width="stretch",
    hide_index=True
)


# ==================================================
# 8. MATCHDAY SUMMARY TABLE
# ==================================================

st.divider()

st.header("Complete Matchday Statistics")

st.dataframe(
    matchday_summary,
    width="stretch",
    hide_index=True
)


# ==================================================
# 9. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Matchday Analysis"
)
