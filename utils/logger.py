
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ==========================================
# PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


# ==========================================
# LOGGER CONFIGURATION
# ==========================================

def get_logger(name):

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    # Αποφυγή διπλών μηνυμάτων
    logger.propagate = False

    # Προσθήκη handlers μόνο μία φορά
    if not logger.handlers:

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger
