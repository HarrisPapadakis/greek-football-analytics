
import streamlit as st

# ==========================================
# 1. APP CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Greek Football Analytics",
    page_icon="⚽",
    layout="wide"
)


# ==========================================
# 2. PAGE DEFINITIONS
# ==========================================

overview_page = st.Page(
    "pages/league_overview.py",
    title="League Overview",
    icon=":material/leaderboard:",
    default=True
)

match_page = st.Page(
    "pages/match_explorer.py",
    title="Match Explorer",
    icon=":material/sports_soccer:"
)

team_analysis_page = st.Page(
    "pages/team_analysis.py",
    title="Team Analysis",
    icon=":material/groups:"
)

team_momentum_page = st.Page(
    "pages/team_momentum.py",
    title="Team Momentum",
    icon=":material/trending_up:"
)

attack_defence_page = st.Page(
    "pages/attack_defence.py",
    title="Attack vs Defence",
    icon=":material/shield:"
)

team_comparison_page = st.Page(
    "pages/team_comparison.py",
    title="Team Comparison",
    icon=":material/compare_arrows:"
)

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Full Dashboard",
    icon=":material/dashboard:"
)

project_page = st.Page(
    "pages/project_info.py",
    title="Project Information",
    icon=":material/info:"
)


# ==========================================
# 3. NAVIGATION
# ==========================================

pg = st.navigation(
    {
        "FOOTBALL ANALYTICS": [
            overview_page,
            match_page,
            team_analysis_page,
            team_momentum_page,
            attack_defence_page,
            team_comparison_page,
            dashboard_page
        ],

        "PROJECT": [
            project_page
        ]
    },
    position="sidebar"
)


# ==========================================
# 4. RUN APPLICATION
# ==========================================

pg.run()