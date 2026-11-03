
import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_matches


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("⚽ Greek Football Analytics")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Football Data Analytics Dashboard | "
    "Data Source: API-Football"
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


# ==================================================
# 3. PREPARE DATA
# ==================================================

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

total_goals = int(
    df["home_goals"].sum() +
    df["away_goals"].sum()
)

average_goals = (
    total_goals / len(df)
    if len(df) > 0 else 0
)


# ==================================================
# 4. COMMON TEAM METRICS FUNCTION
# ==================================================

def calculate_team_metrics(team_name, matches):

    home = matches[
        matches["home_team"] == team_name
    ]

    away = matches[
        matches["away_team"] == team_name
    ]

    # Home results
    home_wins = int(
        (home["home_goals"] > home["away_goals"]).sum()
    )

    home_draws = int(
        (home["home_goals"] == home["away_goals"]).sum()
    )

    home_losses = int(
        (home["home_goals"] < home["away_goals"]).sum()
    )

    # Away results
    away_wins = int(
        (away["away_goals"] > away["home_goals"]).sum()
    )

    away_draws = int(
        (away["away_goals"] == away["home_goals"]).sum()
    )

    away_losses = int(
        (away["away_goals"] < away["home_goals"]).sum()
    )

    # Played
    home_played = len(home)
    away_played = len(away)

    played = home_played + away_played

    # Points
    home_points = home_wins * 3 + home_draws
    away_points = away_wins * 3 + away_draws

    # Goals
    home_goals = int(home["home_goals"].sum())
    away_goals = int(away["away_goals"].sum())

    home_conceded = int(home["away_goals"].sum())
    away_conceded = int(away["home_goals"].sum())

    goals_for = home_goals + away_goals
    goals_against = home_conceded + away_conceded

    # Clean Sheets
    home_clean_sheets = int(
        (home["away_goals"] == 0).sum()
    )

    away_clean_sheets = int(
        (away["home_goals"] == 0).sum()
    )

    total_clean_sheets = (
        home_clean_sheets + away_clean_sheets
    )

    clean_percentage = (
        total_clean_sheets / played * 100
        if played > 0 else 0
    )

    # Goals per Match
    goals_per_match = (
        goals_for / played
        if played > 0 else 0
    )

    conceded_per_match = (
        goals_against / played
        if played > 0 else 0
    )

    return {
        "Played": played,
        "Wins": home_wins + away_wins,
        "Draws": home_draws + away_draws,
        "Losses": home_losses + away_losses,
        "Points": home_points + away_points,
        "Goals Scored": goals_for,
        "Goals Conceded": goals_against,
        "Goal Difference": goals_for - goals_against,
        "Goals per Match": round(goals_per_match, 2),
        "Goals Conceded per Match": round(
            conceded_per_match, 2
        ),
        "Clean Sheets": total_clean_sheets,
        "Clean Sheet %": round(clean_percentage, 2),

        "Home Played": home_played,
        "Home Wins": home_wins,
        "Home Draws": home_draws,
        "Home Losses": home_losses,
        "Home Goals": home_goals,
        "Home Conceded": home_conceded,
        "Home Points": home_points,
        "Home Clean Sheets": home_clean_sheets,

        "Away Played": away_played,
        "Away Wins": away_wins,
        "Away Draws": away_draws,
        "Away Losses": away_losses,
        "Away Goals": away_goals,
        "Away Conceded": away_conceded,
        "Away Points": away_points,
        "Away Clean Sheets": away_clean_sheets
    }


# ==================================================
# 5. LEAGUE OVERVIEW
# ==================================================

st.header("League Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Matches",
    len(df)
)

col2.metric(
    "Regular Season Matches",
    len(regular)
)

col3.metric(
    "Teams",
    len(teams)
)

col4.metric(
    "Goals per Match",
    f"{average_goals:.2f}"
)


# ==================================================
# 6. MATCH EXPLORER
# ==================================================

st.divider()

st.header("Match Explorer")

filter_col1, filter_col2 = st.columns(2)

phases = sorted(
    df["round"].str.split(" - ").str[0].dropna().unique()
)

with filter_col1:

    selected_phase = st.selectbox(
        "Select Competition Phase",
        ["All Phases"] + phases
    )

with filter_col2:

    selected_team = st.selectbox(
        "Select Team",
        ["All Teams"] + teams
    )


# Apply filters
filtered = df.copy()

if selected_phase != "All Phases":

    filtered = filtered[
        filtered["round"].str.startswith(
            selected_phase,
            na=False
        )
    ]

if selected_team != "All Teams":

    filtered = filtered[
        (filtered["home_team"] == selected_team) |
        (filtered["away_team"] == selected_team)
    ]


st.subheader("Filtered Results")

filtered_goals = (
    filtered["home_goals"].sum() +
    filtered["away_goals"].sum()
)

filtered_average = (
    filtered_goals / len(filtered)
    if len(filtered) > 0 else 0
)

m1, m2 = st.columns(2)

m1.metric(
    "Number of Matches",
    len(filtered)
)

m2.metric(
    "Average Goals per Match",
    f"{filtered_average:.2f}"
)


# Matches table
display_df = filtered.sort_values(
    "date",
    ascending=False
).copy()

display_df["Score"] = display_df.apply(
    lambda row: (
        f"{int(row['home_goals'])} - {int(row['away_goals'])}"
        if pd.notna(row["home_goals"])
        and pd.notna(row["away_goals"])
        else "-"
    ),
    axis=1
)

display_df["date"] = display_df["date"].dt.strftime(
    "%d/%m/%Y %H:%M"
)

display_columns = [
    "date",
    "round",
    "home_team",
    "Score",
    "away_team"
]

st.dataframe(
    display_df[display_columns],
    width="stretch",
    hide_index=True
)


# ==================================================
# 7. TEAM GOALS COMPARISON
# ==================================================

st.divider()

st.header("Team Goals Comparison")

st.caption(
    "Total goals scored by each team "
    "during the Regular Season (26 matches)."
)

home_goals_by_team = (
    regular.groupby("home_team")["home_goals"].sum()
)

away_goals_by_team = (
    regular.groupby("away_team")["away_goals"].sum()
)

goals_by_team = (
    pd.concat([
        home_goals_by_team,
        away_goals_by_team
    ])
    .groupby(level=0)
    .sum()
    .astype(int)
)

goals_table = (
    goals_by_team
    .sort_values(ascending=False)
    .rename_axis("Team")
    .reset_index(name="Goals Scored")
)

max_goals = int(
    goals_table["Goals Scored"].max()
)

axis_max = ((max_goals // 5) + 1) * 5

goals_chart = alt.Chart(goals_table).mark_bar().encode(

    x=alt.X(
        "Goals Scored:Q",
        title="Goals Scored",
        scale=alt.Scale(
            domain=[0, axis_max],
            nice=False
        ),
        axis=alt.Axis(
            values=list(range(0, axis_max + 1, 5))
        )
    ),

    y=alt.Y(
        "Team:N",
        sort=alt.SortField(
            field="Goals Scored",
            order="descending"
        ),
        title="Team"
    ),

    tooltip=[
        "Team",
        "Goals Scored"
    ]

).properties(
    height=450,
    title="Goals Scored by Team"
)

st.altair_chart(
    goals_chart,
    width="stretch"
)

st.subheader("Goals Ranking")

st.dataframe(
    goals_table,
    width="stretch",
    hide_index=True
)


# ==================================================
# 8. TEAM ANALYSIS
# ==================================================

st.divider()

st.header("Team Analysis")

selected_analysis_team = st.selectbox(
    "Select Team for Detailed Analysis",
    teams,
    key="team_analysis_select"
)

team_stats = calculate_team_metrics(
    selected_analysis_team,
    regular
)

st.subheader(selected_analysis_team)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Played", team_stats["Played"])
k2.metric("Points", team_stats["Points"])
k3.metric("Goals Scored", team_stats["Goals Scored"])
k4.metric("Goals Conceded", team_stats["Goals Conceded"])


# Additional KPIs
st.subheader("Performance Metrics")

p1, p2, p3, p4 = st.columns(4)

p1.metric("Wins", team_stats["Wins"])
p2.metric("Draws", team_stats["Draws"])
p3.metric("Losses", team_stats["Losses"])
p4.metric(
    "Clean Sheets %",
    f'{team_stats["Clean Sheet %"]:.2f}%'
)


# Home vs Away
st.subheader("Home vs Away Performance")

home_away_table = pd.DataFrame({

    "Venue": ["Home", "Away"],

    "Played": [
        team_stats["Home Played"],
        team_stats["Away Played"]
    ],

    "Wins": [
        team_stats["Home Wins"],
        team_stats["Away Wins"]
    ],

    "Draws": [
        team_stats["Home Draws"],
        team_stats["Away Draws"]
    ],

    "Losses": [
        team_stats["Home Losses"],
        team_stats["Away Losses"]
    ],

    "Goals Scored": [
        team_stats["Home Goals"],
        team_stats["Away Goals"]
    ],

    "Goals Conceded": [
        team_stats["Home Conceded"],
        team_stats["Away Conceded"]
    ],

    "Points": [
        team_stats["Home Points"],
        team_stats["Away Points"]
    ],

    "Clean Sheets": [
        team_stats["Home Clean Sheets"],
        team_stats["Away Clean Sheets"]
    ]

})

st.dataframe(
    home_away_table,
    width="stretch",
    hide_index=True
)


# Team goals chart
st.subheader("Goals Scored vs Conceded")

team_goals_data = pd.DataFrame({

    "Venue": ["Home", "Away"],

    "Goals Scored": [
        team_stats["Home Goals"],
        team_stats["Away Goals"]
    ],

    "Goals Conceded": [
        team_stats["Home Conceded"],
        team_stats["Away Conceded"]
    ]

}).melt(
    id_vars="Venue",
    var_name="Metric",
    value_name="Goals"
)

team_goals_chart = alt.Chart(
    team_goals_data
).mark_bar().encode(

    x=alt.X(
        "Goals:Q",
        title="Goals"
    ),

    y=alt.Y(
        "Venue:N",
        title="Venue"
    ),

    color=alt.Color(
        "Metric:N",
        title="Metric"
    ),

    yOffset="Metric:N",

    tooltip=[
        "Venue",
        "Metric",
        "Goals"
    ]

).properties(
    height=180
)

st.altair_chart(
    team_goals_chart,
    width="stretch"
)


# ==================================================
# 9. TEAM COMPARISON
# ==================================================

st.divider()

st.header("Team Comparison")

st.caption(
    "Compare two teams using Regular Season performance."
)

compare_col1, compare_col2 = st.columns(2)

default_a = (
    teams.index("AEK Athens FC")
    if "AEK Athens FC" in teams else 0
)

default_b = (
    teams.index("Olympiakos Piraeus")
    if "Olympiakos Piraeus" in teams else min(1, len(teams)-1)
)

with compare_col1:

    team_a = st.selectbox(
        "First Team",
        teams,
        index=default_a,
        key="comparison_team_a"
    )

with compare_col2:

    team_b = st.selectbox(
        "Second Team",
        teams,
        index=default_b,
        key="comparison_team_b"
    )


if team_a == team_b:

    st.warning(
        "Please select two different teams."
    )

else:

    stats_a = calculate_team_metrics(team_a, regular)

    stats_b = calculate_team_metrics(team_b, regular)

    comparison_metrics = [
        "Played",
        "Wins",
        "Draws",
        "Losses",
        "Points",
        "Goals Scored",
        "Goals Conceded",
        "Goal Difference",
        "Goals per Match",
        "Goals Conceded per Match",
        "Clean Sheets",
        "Clean Sheet %"
    ]

    comparison_table = pd.DataFrame({

        "Metric": comparison_metrics,

        team_a: [
            stats_a[metric]
            for metric in comparison_metrics
        ],

        team_b: [
            stats_b[metric]
            for metric in comparison_metrics
        ]

    })

    st.subheader(
        f"{team_a} vs {team_b}"
    )

    st.dataframe(
        comparison_table,
        width="stretch",
        hide_index=True
    )


    # Points comparison
    st.subheader("Points Comparison")

    points_data = pd.DataFrame({

        "Team": [team_a, team_b],

        "Points": [
            stats_a["Points"],
            stats_b["Points"]
        ]

    })

    points_chart = alt.Chart(
        points_data
    ).mark_bar().encode(

        x=alt.X(
            "Points:Q",
            title="Points"
        ),

        y=alt.Y(
            "Team:N",
            sort="-x"
        ),

        tooltip=["Team", "Points"]

    ).properties(
        height=150
    )

    st.altair_chart(
        points_chart,
        width="stretch"
    )


    # Goals comparison
    st.subheader("Goals Comparison")

    goals_comparison_data = pd.DataFrame({

        "Team": [
            team_a, team_a,
            team_b, team_b
        ],

        "Metric": [
            "Goals Scored",
            "Goals Conceded",
            "Goals Scored",
            "Goals Conceded"
        ],

        "Goals": [
            stats_a["Goals Scored"],
            stats_a["Goals Conceded"],
            stats_b["Goals Scored"],
            stats_b["Goals Conceded"]
        ]

    })

    goals_comparison_chart = alt.Chart(
        goals_comparison_data
    ).mark_bar().encode(

        x=alt.X(
            "Goals:Q",
            title="Goals"
        ),

        y=alt.Y(
            "Team:N",
            sort=[team_a, team_b]
        ),

        yOffset="Metric:N",

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
        height=180
    )

    st.altair_chart(
        goals_comparison_chart,
        width="stretch"
    )


    # Automatic comparison
    points_difference = abs(
        stats_a["Points"] - stats_b["Points"]
    )

    if stats_a["Points"] > stats_b["Points"]:

        st.info(
            f"{team_a} has {points_difference} more points "
            f"than {team_b}."
        )

    elif stats_b["Points"] > stats_a["Points"]:

        st.info(
            f"{team_b} has {points_difference} more points "
            f"than {team_a}."
        )

    else:

        st.info(
            "Both teams have the same number of points."
        )


# ==================================================
# 10. LEAGUE STANDINGS
# ==================================================

st.divider()

st.header("League Standings")

st.caption(
    "Super League Greece 2024-25 | Regular Season"
)

standings_rows = []

for team in teams:

    stats = calculate_team_metrics(
        team,
        regular
    )

    standings_rows.append({

        "Team": team,
        "Played": stats["Played"],
        "Wins": stats["Wins"],
        "Draws": stats["Draws"],
        "Losses": stats["Losses"],
        "GF": stats["Goals Scored"],
        "GA": stats["Goals Conceded"],
        "GD": stats["Goal Difference"],
        "Points": stats["Points"]

    })


standings = pd.DataFrame(standings_rows)

standings = standings.sort_values(

    ["Points", "GD", "GF"],

    ascending=[False, False, False]

).reset_index(drop=True)


standings.insert(
    0,
    "Pos",
    range(1, len(standings) + 1)
)


st.dataframe(
    standings,
    width="stretch",
    hide_index=True
)

st.caption(
    "Analytical ranking: Points → Goal Difference → Goals For. "
    "This is a calculated ranking, not a verification of every "
    "official tie-break rule."
)


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics Portfolio Project | "
    "Python • Pandas • Streamlit • Altair"
)
