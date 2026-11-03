
import streamlit as st
import pandas as pd

from utils.data_loader import load_matches


# ==================================================
# 1. PAGE HEADER
# ==================================================

st.title("⚽ Match Explorer")

st.subheader("Super League Greece 2024-25")

st.caption(
    "Search, filter and explore matches "
    "from the Greek Super League."
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


# Αφαιρούμε αγώνες χωρίς τελικό σκορ
df = df.dropna(
    subset=["home_goals", "away_goals", "date"]
).copy()

# Δημιουργία πεδίων ημερομηνίας και φάσης
df["match_date"] = df["date"].dt.date

df["phase"] = (
    df["round"]
    .str.rsplit(" - ", n=1)
    .str[0]
    .fillna("Unknown")
)

teams = sorted(
    set(df["home_team"].dropna()) |
    set(df["away_team"].dropna())
)

phases = sorted(
    df["phase"].dropna().unique()
)


# ==================================================
# 3. FILTERS
# ==================================================

st.header("Match Filters")

col1, col2 = st.columns(2)

with col1:

    selected_phase = st.selectbox(
        "Competition Phase",
        ["All Phases"] + phases
    )

    selected_team = st.selectbox(
        "Team",
        ["All Teams"] + teams
    )

with col2:

    selected_result = st.selectbox(
        "Match Result",
        [
            "All Results",
            "Home Win",
            "Draw",
            "Away Win"
        ]
    )

    search_text = st.text_input(
        "Search Team, Referee or Venue",
        placeholder="Example: AEK, Olympiakos..."
    )


# ==================================================
# 4. DATE FILTER
# ==================================================

st.subheader("Date Range")

min_date = df["match_date"].min()
max_date = df["match_date"].max()

date_range = st.date_input(
    "Select Match Dates",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)

# ==================================================
# 5. APPLY FILTERS
# ==================================================

filtered = df.copy()

# Competition phase
if selected_phase != "All Phases":

    filtered = filtered[
        filtered["phase"] == selected_phase
    ]

# Team
if selected_team != "All Teams":

    filtered = filtered[
        (filtered["home_team"] == selected_team) |
        (filtered["away_team"] == selected_team)
    ]

# Result
if selected_result == "Home Win":

    filtered = filtered[
        filtered["home_goals"] > filtered["away_goals"]
    ]

elif selected_result == "Draw":

    filtered = filtered[
        filtered["home_goals"] == filtered["away_goals"]
    ]

elif selected_result == "Away Win":

    filtered = filtered[
        filtered["home_goals"] < filtered["away_goals"]
    ]

# Date range
if isinstance(date_range, (tuple, list)):

    if len(date_range) == 2:

        start_date, end_date = date_range

    elif len(date_range) == 1:

        start_date = end_date = date_range[0]

    else:

        start_date = end_date = None

elif date_range is not None:

    start_date = end_date = date_range

else:

    start_date = end_date = None


if start_date is not None and end_date is not None:

    filtered = filtered[
        filtered["match_date"].between(
            start_date,
            end_date
        )
    ]

# Search
if search_text.strip():

    search_mask = pd.Series(
        False,
        index=filtered.index
    )

    search_columns = [
        "home_team",
        "away_team",
        "referee",
        "venue"
    ]

    for column in search_columns:

        if column in filtered.columns:

            search_mask |= (
                filtered[column]
                .fillna("")
                .astype(str)
                .str.contains(
                    search_text.strip(),
                    case=False,
                    regex=False
                )
            )

    filtered = filtered[search_mask]


# ==================================================
# 6. MATCH STATISTICS
# ==================================================

st.divider()

st.header("Search Results")

number_of_matches = len(filtered)

total_goals = int(
    filtered["home_goals"].sum() +
    filtered["away_goals"].sum()
)

average_goals = (
    total_goals / number_of_matches
    if number_of_matches > 0 else 0
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Matches Found",
    number_of_matches
)

c2.metric(
    "Total Goals",
    total_goals
)

c3.metric(
    "Goals per Match",
    f"{average_goals:.2f}"
)


# ==================================================
# 7. MATCH TABLE
# ==================================================

st.subheader("Match Results")

if not filtered.empty:

    display_df = filtered.sort_values(
        "date",
        ascending=False
    ).copy()

    # Δημιουργία αποτελέσματος
    display_df["Score"] = display_df.apply(
        lambda row: (
            f"{int(row['home_goals'])} - "
            f"{int(row['away_goals'])}"
        ),
        axis=1
    )

    display_df["Date"] = (
        display_df["date"]
        .dt.strftime("%d/%m/%Y %H:%M")
    )

    display_df["Home Team"] = display_df["home_team"]
    display_df["Away Team"] = display_df["away_team"]

    display_df["Competition Phase"] = display_df["phase"]
    display_df["Round"] = display_df["round"]

    display_columns = [
        "Date",
        "Competition Phase",
        "Round",
        "Home Team",
        "Score",
        "Away Team"
    ]

    # Προαιρετικές πληροφορίες
    if "referee" in display_df.columns:
        display_columns.append("referee")

    if "venue" in display_df.columns:
        display_columns.append("venue")

    result_table = display_df[display_columns].rename(
        columns={
            "referee": "Referee",
            "venue": "Venue"
        }
    )

    st.dataframe(
        result_table,
        width="stretch",
        hide_index=True
    )

    # Download filtered matches
    csv_data = result_table.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Download Filtered Matches CSV",
        data=csv_data,
        file_name="filtered_matches.csv",
        mime="text/csv"
    )

else:

    st.warning(
        "No matches found. Try changing your filters."
    )


# ==================================================
# 8. FOOTER
# ==================================================

st.divider()

st.caption(
    "Greek Football Analytics | Match Explorer"
)
