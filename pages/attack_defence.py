import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.attack_defence_analysis import (
    build_attack_defence_summary,
)


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("⚽ Attack vs Defence Analysis")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Comparing attacking output and defensive performance "
    "| Regular Season"
)

st.divider()


# ==================================================
# 2. LOAD DATA
# ==================================================

try:
    df = load_matches()

    regular = df[
        df["round"].str.startswith(
            "Regular Season",
            na=False
        )
    ].dropna(
        subset=["home_goals", "away_goals"]
    ).copy()

    summary = build_attack_defence_summary(regular)

except Exception as error:
    st.exception(error)
    st.stop()


if summary.empty:
    st.error("No team performance data available.")
    st.stop()


# ==================================================
# 3. LEAGUE METRICS
# ==================================================

st.header("League Overview")

league_average = float(
    summary["League Average"].iloc[0]
)

top_attack = summary.sort_values(
    "Goals per Match",
    ascending=False
).iloc[0]

top_defence = summary.sort_values(
    "Goals Conceded per Match",
    ascending=True
).iloc[0]

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Teams Analysed",
    len(summary)
)

k2.metric(
    "Matches Analysed",
    len(regular)
)

k3.metric(
    "League Goals per Team / Match",
    f"{league_average:.2f}"
)

k4.metric(
    "League Goals per Match",
    f"{league_average * 2:.2f}"
)


# ==================================================
# 4. TOP ATTACK AND DEFENCE
# ==================================================

st.divider()

st.header("Attacking and Defensive Leaders")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Best Attack")

    st.metric(
        "Team",
        top_attack["Team"]
    )

    st.metric(
        "Goals per Match",
        f'{top_attack["Goals per Match"]:.2f}'
    )

with c2:
    st.subheader("Best Defence")

    st.metric(
        "Team",
        top_defence["Team"]
    )

    st.metric(
        "Goals Conceded per Match",
        f'{top_defence["Goals Conceded per Match"]:.2f}'
    )


# ==================================================
# 5. ATTACK VS DEFENCE CLASSIFICATION
# ==================================================

st.divider()

st.header("Attack vs Defence Matrix")

st.caption(
    "Teams are compared against the league average. "
    "Strong defence means conceding fewer goals per match "
    "than the league average."
)


def classify_performance(row):

    strong_attack = (
        row["Goals per Match"] >= league_average
    )

    strong_defence = (
        row["Goals Conceded per Match"] <= league_average
    )

    if strong_attack and strong_defence:
        return "Strong Attack & Defence"

    elif strong_attack:
        return "Strong Attack"

    elif strong_defence:
        return "Strong Defence"

    return "Below Average in Both"


chart_data = summary.copy()

chart_data["Performance Profile"] = (
    chart_data.apply(
        classify_performance,
        axis=1
    )
)


# Scatter plot
points = alt.Chart(
    chart_data
).mark_circle(
    size=150,
    opacity=0.85
).encode(

    x=alt.X(
        "Goals per Match:Q",
        title="Goals Scored per Match",
        scale=alt.Scale(zero=False)
    ),

    y=alt.Y(
        "Goals Conceded per Match:Q",
        title="Goals Conceded per Match (lower is better)",
        scale=alt.Scale(zero=False)
    ),

    color=alt.Color(
        "Performance Profile:N",
        title="Performance Profile"
    ),

    tooltip=[
        alt.Tooltip("Team:N"),
        alt.Tooltip("Matches:Q"),
        alt.Tooltip("Goals per Match:Q", format=".2f"),
        alt.Tooltip(
            "Goals Conceded per Match:Q",
            format=".2f"
        ),
        alt.Tooltip("Attack Rank:Q"),
        alt.Tooltip("Defence Rank:Q"),
        alt.Tooltip("Performance Profile:N")
    ]

)


# League average reference lines
average_x = alt.Chart(
    pd.DataFrame({
        "average": [league_average]
    })
).mark_rule(
    strokeDash=[6, 4]
).encode(
    x="average:Q"
)


average_y = alt.Chart(
    pd.DataFrame({
        "average": [league_average]
    })
).mark_rule(
    strokeDash=[6, 4]
).encode(
    y="average:Q"
)


# Team labels
labels = alt.Chart(
    chart_data
).mark_text(
    dy=-12,
    fontSize=10
).encode(
    x="Goals per Match:Q",
    y="Goals Conceded per Match:Q",
    text="Team:N"
)


attack_defence_chart = (
    points + average_x + average_y + labels
).properties(
    height=480,
    title="Attacking Output vs Defensive Performance"
).interactive()


st.altair_chart(
    attack_defence_chart,
    width="stretch"
)


st.caption(
    "Interpretation: Teams in the lower-right area combine "
    "above-average scoring with below-average goals conceded."
)


# ==================================================
# 6. TEAM PERFORMANCE TABLE
# ==================================================

st.divider()

st.header("Detailed Team Performance")

display_columns = [
    "Team",
    "Matches",
    "Goals Scored",
    "Goals Conceded",
    "Goals per Match",
    "Goals Conceded per Match",
    "Scoring Matches %",
    "Clean Sheets",
    "Clean Sheet %",
    "Attack Rank",
    "Defence Rank"
]

st.dataframe(
    summary[display_columns],
    width="stretch",
    hide_index=True
)


# ==================================================
# 7. ATTACK AND DEFENCE RANKINGS
# ==================================================

st.divider()

st.header("Separate Performance Rankings")

attack_col, defence_col = st.columns(2)

with attack_col:

    st.subheader("Top 5 Attacking Teams")

    attack_ranking = summary.sort_values(
        ["Goals per Match", "Team"],
        ascending=[False, True]
    ).head(5)

    st.dataframe(
        attack_ranking[
            [
                "Team",
                "Goals Scored",
                "Goals per Match",
                "Scoring Matches %"
            ]
        ],
        width="stretch",
        hide_index=True
    )


with defence_col:

    st.subheader("Top 5 Defensive Teams")

    defence_ranking = summary.sort_values(
        ["Goals Conceded per Match", "Team"],
        ascending=[True, True]
    ).head(5)

    st.dataframe(
        defence_ranking[
            [
                "Team",
                "Goals Conceded",
                "Goals Conceded per Match",
                "Clean Sheet %"
            ]
        ],
        width="stretch",
        hide_index=True
    )


# ==================================================
# 8. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Attack vs Defence Analysis"
)