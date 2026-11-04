
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.momentum_analysis import (
    build_league_momentum,
    build_momentum_summary,
)


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("📈 Team Momentum")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Tracking team performance through rolling points "
    "per match over the last five completed matches."
)

st.divider()


# ==================================================
# 2. LOAD DATA
# ==================================================

try:
    df = load_matches()

    momentum = build_league_momentum(
        df,
        window=5
    )

    summary = build_momentum_summary(momentum)

except Exception as error:
    st.exception(error)
    st.stop()


if summary.empty:
    st.warning("No momentum data available.")
    st.stop()


# ==================================================
# 3. LEAGUE MOMENTUM KPIs
# ==================================================

st.header("League Momentum Overview")

top_teams = summary.loc[
    summary["Position"] == 1,
    "Team"
].tolist()

highest_momentum = summary["Points per Match"].max()

k1, k2, k3 = st.columns(3)

k1.metric(
    "Teams Analysed",
    len(summary)
)

k2.metric(
    "Highest Momentum",
    f"{highest_momentum:.2f}",
    help="Points per match over the latest five completed matches."
)

k3.metric(
    "Top Teams",
    ", ".join(top_teams)
)


# ==================================================
# 4. MOMENTUM RANKING
# ==================================================

st.divider()

st.header("Team Momentum Ranking")

st.caption(
    "Teams are ranked by points per match over their latest "
    "five completed matches. Ties are separated by total points "
    "and goal difference."
)

ranking = summary.copy()

ranking["Last Match"] = pd.to_datetime(
    ranking["Last Match"]
).dt.strftime("%d/%m/%Y")

st.dataframe(
    ranking,
    width="stretch",
    hide_index=True,
    column_config={
        "Position": st.column_config.NumberColumn(
            "Position",
            format="%d"
        ),
        "Points per Match": st.column_config.NumberColumn(
            "Points per Match",
            format="%.2f"
        ),
        "Goal Difference": st.column_config.NumberColumn(
            "Goal Difference",
            format="%+d"
        ),
    }
)


# ==================================================
# 5. TEAM SELECTION
# ==================================================

st.divider()

st.header("Compare Team Momentum")

top_five_teams = summary["Team"].head(5).tolist()

selected_teams = st.multiselect(
    "Select teams to compare",
    options=summary["Team"].tolist(),
    default=top_five_teams
)

if not selected_teams:
    st.info("Select at least one team to display the chart.")
    st.stop()


# ==================================================
# 6. MOMENTUM EVOLUTION CHART
# ==================================================

st.subheader("Momentum Evolution")

st.caption(
    "Rolling points per match. Only complete five-match "
    "windows are displayed, ensuring comparable measurements."
)

chart_data = momentum[
    (momentum["team"].isin(selected_teams))
    & (momentum["matches_in_window"] == 5)
].copy()

if chart_data.empty:
    st.info("No complete five-match windows available.")
else:

    momentum_chart = alt.Chart(
        chart_data
    ).mark_line(
        point=True,
        strokeWidth=2
    ).encode(

        x=alt.X(
            "date:T",
            title="Match Date",
            axis=alt.Axis(format="%d/%m/%Y")
        ),

        y=alt.Y(
            "rolling_points_per_match:Q",
            title="Points per Match",
            scale=alt.Scale(
                domain=[0, 3]
            )
        ),

        color=alt.Color(
            "team:N",
            title="Team"
        ),

        tooltip=[
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip(
                "rolling_points_per_match:Q",
                title="Points per Match",
                format=".2f"
            ),
            alt.Tooltip(
                "rolling_points:Q",
                title="Points Last 5"
            ),
            alt.Tooltip(
                "form_last_5:N",
                title="Last 5 Results"
            ),
            alt.Tooltip(
                "goal_difference_last_5:Q",
                title="Goal Difference"
            )
        ]

    ).properties(
        height=420
    ).interactive()

    st.altair_chart(
        momentum_chart,
        width="stretch"
    )


# ==================================================
# 7. TEAM FORM DETAILS
# ==================================================

st.divider()

st.header("Latest Team Form")

latest_details = summary[
    summary["Team"].isin(selected_teams)
].copy()

latest_details["Last Match"] = pd.to_datetime(
    latest_details["Last Match"]
).dt.strftime("%d/%m/%Y")

st.dataframe(
    latest_details,
    width="stretch",
    hide_index=True
)


# ==================================================
# 8. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Team Momentum"
)
