
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches
from utils.team_metrics import calculate_team_metrics


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("⚽ Team Comparison")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Head-to-head statistical comparison | Regular Season"
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

if len(teams) < 2:
    st.error("At least two teams are required.")
    st.stop()


# ==================================================
# 3. TEAM SELECTION
# ==================================================

st.header("Select Teams")

col1, col2 = st.columns(2)

default_a = (
    teams.index("AEK Athens FC")
    if "AEK Athens FC" in teams else 0
)

default_b = (
    teams.index("Olympiakos Piraeus")
    if "Olympiakos Piraeus" in teams else 1
)

with col1:
    team_a = st.selectbox(
        "First Team",
        teams,
        index=default_a,
        key="comparison_team_a"
    )

with col2:
    team_b = st.selectbox(
        "Second Team",
        teams,
        index=default_b,
        key="comparison_team_b"
    )


# ==================================================
# 4. CALCULATE METRICS
# ==================================================

if team_a == team_b:

    st.warning("Please select two different teams.")

else:

    stats_a = calculate_team_metrics(
        regular,
        team_a
    )

    stats_b = calculate_team_metrics(
        regular,
        team_b
    )

    overall_a = stats_a["overall"]
    overall_b = stats_b["overall"]


    # ==============================================
    # 5. PERFORMANCE OVERVIEW
    # ==============================================

    st.divider()

    st.header("Performance Overview")

    team_col1, team_col2 = st.columns(2)

    with team_col1:

        st.subheader(team_a)

        c1, c2 = st.columns(2)

        c1.metric(
            "Matches",
            overall_a["matches_played"]
        )

        c2.metric(
            "Points",
            overall_a["points"]
        )

        c3, c4 = st.columns(2)

        c3.metric(
            "Goals Scored",
            overall_a["goals_scored"]
        )

        c4.metric(
            "Goals Conceded",
            overall_a["goals_conceded"]
        )

    with team_col2:

        st.subheader(team_b)

        c1, c2 = st.columns(2)

        c1.metric(
            "Matches",
            overall_b["matches_played"]
        )

        c2.metric(
            "Points",
            overall_b["points"]
        )

        c3, c4 = st.columns(2)

        c3.metric(
            "Goals Scored",
            overall_b["goals_scored"]
        )

        c4.metric(
            "Goals Conceded",
            overall_b["goals_conceded"]
        )


    # ==============================================
    # 6. DETAILED STATISTICS
    # ==============================================

    st.divider()

    st.header("Detailed Statistics")

    metrics = [
        ("Matches Played", "matches_played"),
        ("Wins", "wins"),
        ("Draws", "draws"),
        ("Losses", "losses"),
        ("Points", "points"),
        ("Goals Scored", "goals_scored"),
        ("Goals Conceded", "goals_conceded"),
        ("Goal Difference", "goal_difference"),
        ("Goals per Match", "goals_per_match"),
        ("Goals Conceded per Match", "goals_conceded_per_match"),
        ("Clean Sheets", "clean_sheets"),
        ("Clean Sheet Percentage", "clean_sheet_percentage")
    ]

    comparison_table = pd.DataFrame({

        "Metric": [
            item[0] for item in metrics
        ],

        team_a: [
            overall_a[item[1]] for item in metrics
        ],

        team_b: [
            overall_b[item[1]] for item in metrics
        ]

    })

    st.dataframe(
        comparison_table,
        width="stretch",
        hide_index=True
    )


    # ==============================================
    # 7. POINTS COMPARISON
    # ==============================================

    st.divider()

    st.header("Points Comparison")

    points_data = pd.DataFrame({

        "Team": [team_a, team_b],

        "Points": [
            overall_a["points"],
            overall_b["points"]
        ]

    })

    points_chart = alt.Chart(
        points_data
    ).mark_bar().encode(

        x=alt.X(
            "Points:Q",
            title="Points",
            scale=alt.Scale(domainMin=0)
        ),

        y=alt.Y(
            "Team:N",
            sort="-x",
            title="Team"
        ),

        tooltip=[
            "Team",
            "Points"
        ]

    ).properties(
        height=180
    )

    st.altair_chart(
        points_chart,
        width="stretch"
    )


    # ==============================================
    # 8. GOALS COMPARISON
    # ==============================================

    st.divider()

    st.header("Goals Comparison")

    goals_data = pd.DataFrame({

        "Team": [
            team_a,
            team_a,
            team_b,
            team_b
        ],

        "Metric": [
            "Goals Scored",
            "Goals Conceded",
            "Goals Scored",
            "Goals Conceded"
        ],

        "Goals": [
            overall_a["goals_scored"],
            overall_a["goals_conceded"],
            overall_b["goals_scored"],
            overall_b["goals_conceded"]
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
            "Team:N",
            sort=[team_a, team_b],
            title="Team"
        ),

        yOffset=alt.YOffset("Metric:N"),

        color=alt.Color(
            "Metric:N",
            title="Metric"
        ),

        tooltip=[
            "Team",
            "Metric",
            "Goals"
        ]

    ).properties(
        height=220
    )

    st.altair_chart(
        goals_chart,
        width="stretch"
    )


    # ==============================================
    # 9. HOME VS AWAY COMPARISON
    # ==============================================

    st.divider()

    st.header("Home vs Away Comparison")

    home_away_table = pd.DataFrame({

        "Metric": [
            "Points",
            "Goals Scored",
            "Goals Conceded",
            "Clean Sheets",
            "Clean Sheet %"
        ],

        f"{team_a} Home": [
            stats_a["home"]["points"],
            stats_a["home"]["goals_scored"],
            stats_a["home"]["goals_conceded"],
            stats_a["home"]["clean_sheets"],
            stats_a["home"]["clean_sheet_percentage"]
        ],

        f"{team_a} Away": [
            stats_a["away"]["points"],
            stats_a["away"]["goals_scored"],
            stats_a["away"]["goals_conceded"],
            stats_a["away"]["clean_sheets"],
            stats_a["away"]["clean_sheet_percentage"]
        ],

        f"{team_b} Home": [
            stats_b["home"]["points"],
            stats_b["home"]["goals_scored"],
            stats_b["home"]["goals_conceded"],
            stats_b["home"]["clean_sheets"],
            stats_b["home"]["clean_sheet_percentage"]
        ],

        f"{team_b} Away": [
            stats_b["away"]["points"],
            stats_b["away"]["goals_scored"],
            stats_b["away"]["goals_conceded"],
            stats_b["away"]["clean_sheets"],
            stats_b["away"]["clean_sheet_percentage"]
        ]

    })

    st.dataframe(
        home_away_table,
        width="stretch",
        hide_index=True
    )


    # ==============================================
    # 10. COMPARISON SUMMARY
    # ==============================================

    st.divider()

    st.header("Comparison Summary")

    points_difference = abs(
        overall_a["points"] - overall_b["points"]
    )

    goals_difference = abs(
        overall_a["goals_scored"] - overall_b["goals_scored"]
    )

    clean_difference = abs(
        overall_a["clean_sheet_percentage"] -
        overall_b["clean_sheet_percentage"]
    )

    if overall_a["points"] > overall_b["points"]:

        st.info(
            f"{team_a} collected {points_difference} "
            f"more points than {team_b}."
        )

    elif overall_b["points"] > overall_a["points"]:

        st.info(
            f"{team_b} collected {points_difference} "
            f"more points than {team_a}."
        )

    else:

        st.info(
            "Both teams have the same number of points."
        )

    st.write(
        f"Difference in goals scored: {goals_difference}"
    )

    st.write(
        f"Difference in Clean Sheet Percentage: "
        f"{clean_difference:.2f} percentage points"
    )


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Team Comparison"
)
