
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.logger import get_logger


# ==========================================
# 1. LOGGER
# ==========================================

logger = get_logger(__name__)


# ==========================================
# 2. PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "processed"

MATCHES_FILE = DATA_DIR / "matches.csv"


# ==========================================
# 3. LOAD MATCHES
# ==========================================

@st.cache_data
def load_matches():

    logger.info(
        "Starting dataset loading: %s",
        MATCHES_FILE
    )

    # Έλεγχος ύπαρξης αρχείου
    if not MATCHES_FILE.exists():

        error_message = (
            f"Dataset file not found: {MATCHES_FILE}"
        )

        logger.error(error_message)

        raise FileNotFoundError(error_message)

    # Ανάγνωση CSV
    try:

        df = pd.read_csv(
            MATCHES_FILE,
            encoding="utf-8-sig"
        )

    except Exception:

        logger.exception(
            "Failed to read matches.csv"
        )

        raise

    # Απαραίτητες στήλες
    required_columns = [
        "fixture_id",
        "date",
        "round",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    # Έλεγχος στηλών
    if missing_columns:

        error_message = (
            f"Missing required columns: {missing_columns}"
        )

        logger.error(error_message)

        raise ValueError(error_message)

    # Μετατροπή ημερομηνίας
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        utc=True
    )

    df["date"] = df["date"].dt.tz_convert(
        "Europe/Athens"
    )

    # Μετατροπή γκολ
    df["home_goals"] = pd.to_numeric(
        df["home_goals"],
        errors="coerce"
    )

    df["away_goals"] = pd.to_numeric(
        df["away_goals"],
        errors="coerce"
    )

    # Αντιμετώπιση κενών round
    df["round"] = df["round"].fillna("Unknown")

    # Επιτυχής φόρτωση
    logger.info(
        "Dataset loaded successfully | Rows: %s | Columns: %s",
        len(df),
        len(df.columns)
    )

    return df
