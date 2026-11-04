
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.consistency_analysis import build_consistency_summary


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("📊 Consistency Analysis")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Measuring team performance and match-to-match "
    "consistency | Regular Season"
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

    summary = build_consistency_summary(regular)

except Exception as error:
    st.exception(error)
    st.stop()


if summary.empty:
    st.error("No team consistency data available.")
    st.stop()


# ==================================================
# 3. LEAGUE BENCHMARKS
# ==================================================

league_average_ppm = summary["Points per Match"].mean()

league_average_std = summary["Points Std Dev"].mean()

most_consistent = summary.sort_values(
    ["Points Std Dev", "Points per Match"],
    ascending=[True, False]
).iloc[0]

best_performance = summary.sort_values(
    ["Points per Match", "Points Std Dev"],
    ascending=[False, True]
).iloc[0]


# ==================================================
# 4. LEAGUE OVERVIEW KPIs
# ==================================================

st.header("Consistency Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Teams Analysed",
    len(summary)
)

k2.metric(
    "Matches per Team",
    int(summary["Matches"].min())
)

k3.metric(
    "League Average Points / Match",
    f"{league_average_ppm:.2f}"
)

k4.metric(
    "Average Points Std Dev",
    f"{league_average_std:.3f}"
)


# ==================================================
# 5. PERFORMANCE LEADERS
# ==================================================

st.divider()

st.header("Performance Highlights")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Most Consistent Team")

    st.metric(
        "Team",
        most_consistent["Team"]
    )

    st.metric(
        "Points Standard Deviation",
        f'{most_consistent["Points Std Dev"]:.3f}',
        help="Lower values indicate less variation in points earned per match."
    )

with c2:
    st.subheader("Highest Average Performance")

    st.metric(
        "Team",
        best_performance["Team"]
    )

    st.metric(
        "Points per Match",
        f'{best_performance["Points per Match"]:.2f}'
    )


# ==================================================
# 6. PERFORMANCE CLASSIFICATION
# ==================================================

st.divider()

st.header("Performance vs Consistency Matrix")

st.caption(
    "The vertical benchmark is the league average points per match. "
    "The horizontal benchmark is the average team points standard deviation."
)


def classify_consistency(row):

    above_average_performance = (
        row["Points per Match"] >= league_average_ppm
    )

    below_average_variability = (
        row["Points Std Dev"] <= league_average_std
    )

    if above_average_performance and below_average_variability:
        return "High Performance / Consistent"

    elif above_average_performance:
        return "High Performance / Variable"

    elif below_average_variability:
        return "Lower Performance / Consistent"

    return "Lower Performance / Variable"


chart_data = summary.copy()

chart_data["Performance Profile"] = chart_data.apply(
    classify_consistency,
    axis=1
)


# ==================================================
# 7. SCATTER PLOT
# ==================================================

points = alt.Chart(
    chart_data
).mark_circle(
    size=150,
    opacity=0.85
).encode(

    x=alt.X(
        "Points per Match:Q",
        title="Average Points per Match",
        scale=alt.Scale(domain=[0, 3])
    ),

    y=alt.Y(
        "Points Std Dev:Q",
        title="Points Standard Deviation (lower is more consistent)",
        scale=alt.Scale(domainMin=0)
    ),

    color=alt.Color(
        "Performance Profile:N",
        title="Performance Profile"
    ),

    tooltip=[
        alt.Tooltip("Team:N"),
        alt.Tooltip("Matches:Q"),
        alt.Tooltip(
            "Points per Match:Q",
            format=".2f"
        ),
        alt.Tooltip(
            "Points Std Dev:Q",
            format=".3f"
        ),
        alt.Tooltip(
            "Goal Difference Std Dev:Q",
            format=".3f"
        ),
        alt.Tooltip("Performance Profile:N")
    ]

)


# Average performance reference line
average_performance_line = alt.Chart(
    pd.DataFrame({
        "average": [league_average_ppm]
    })
).mark_rule(
    strokeDash=[6, 4]
).encode(
    x="average:Q"
)


# Average variability reference line
average_consistency_line = alt.Chart(
    pd.DataFrame({
        "average": [league_average_std]
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
    x="Points per Match:Q",
    y="Points Std Dev:Q",
    text="Team:N"
)


consistency_chart = (
    points
    + average_performance_line
    + average_consistency_line
    + labels
).properties(
    height=480,
    title="Team Performance vs Match-to-Match Variability"
).interactive()


st.altair_chart(
    consistency_chart,
    width="stretch"
)


st.caption(
    "Interpretation: The upper-right quadrant combines higher average "
    "points with greater variability. The lower-right quadrant combines "
    "higher average points with lower variability."
)


# ==================================================
# 8. TEAM CONSISTENCY TABLE
# ==================================================

st.divider()

st.header("Detailed Consistency Ranking")

ranking = summary.sort_values(
    [
        "Points Std Dev",
        "Points per Match",
        "Team"
    ],
    ascending=[
        True,
        False,
        True
    ]
).reset_index(drop=True)

ranking.insert(
    0,
    "Variability Rank",
    ranking["Points Std Dev"].rank(
        method="min",
        ascending=True
    ).astype(int)
)

st.dataframe(
    ranking,
    width="stretch",
    hide_index=True,
    column_config={
        "Points per Match": st.column_config.NumberColumn(
            "Points per Match",
            format="%.2f"
        ),
        "Points Std Dev": st.column_config.NumberColumn(
            "Points Std Dev",
            format="%.3f"
        ),
        "Goal Difference Std Dev": st.column_config.NumberColumn(
            "Goal Difference Std Dev",
            format="%.3f"
        ),
    }
)


# ==================================================
# 9. ATTACKING AND DEFENSIVE CONSISTENCY
# ==================================================

st.divider()

st.header("Attacking and Defensive Consistency")

left, right = st.columns(2)

with left:
    st.subheader("Scoring Reliability")

    scoring_ranking = summary.sort_values(
        ["Scoring Matches %", "Team"],
        ascending=[False, True]
    ).head(5)

    st.dataframe(
        scoring_ranking[
            [
                "Team",
                "Scoring Matches %",
                "Points per Match"
            ]
        ],
        width="stretch",
        hide_index=True
    )

with right:
    st.subheader("Clean Sheet Reliability")

    clean_sheet_ranking = summary.sort_values(
        ["Clean Sheet %", "Team"],
        ascending=[False, True]
    ).head(5)

    st.dataframe(
        clean_sheet_ranking[
            [
                "Team",
                "Clean Sheets",
                "Clean Sheet %"
            ]
        ],
        width="stretch",
        hide_index=True
    )


# ==================================================
# 10. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Consistency Analysis"
)
