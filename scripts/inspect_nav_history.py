"""
inspect_nav_history.py
-----------------------
Day 2 - Bluestock Mutual Fund Analytics Capstone.

Profiles the raw NAV history dataset BEFORE any cleaning is performed, so we
have a documented baseline of its shape, quality issues, and value ranges.

Input : data/raw/02_nav_history.csv
Output: data/processed/nav_profile_summary.csv
"""

import logging
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("inspect_nav_history")

# --------------------------------------------------------------------------- #
# Path configuration (pathlib so it works regardless of where it is run from)
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "02_nav_history.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "nav_profile_summary.csv"


def load_dataset(path: Path) -> pd.DataFrame:
    """Load the NAV history CSV into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info("Loading dataset from %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %d rows and %d columns", df.shape[0], df.shape[1])
    return df


def describe_structure(df: pd.DataFrame) -> None:
    """Print the basic structure of the dataset."""
    logger.info("Shape: %s", df.shape)

    logger.info("Column names: %s", list(df.columns))

    logger.info("Data types:\n%s", df.dtypes.to_string())

    logger.info("First 5 rows:\n%s", df.head().to_string())

    logger.info("Last 5 rows:\n%s", df.tail().to_string())


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Compute profiling metrics and return them as an ordered dict so they can be
    persisted to a summary CSV.
    """
    # --- Missing values per column -------------------------------------- #
    missing_per_column = df.isna().sum()
    logger.info("Missing values per column:\n%s", missing_per_column.to_string())

    # --- Duplicate rows ------------------------------------------------- #
    duplicate_rows = int(df.duplicated().sum())
    logger.info("Duplicate rows: %d", duplicate_rows)

    # --- Unique AMFI codes ---------------------------------------------- #
    unique_amfi_codes = int(df["amfi_code"].nunique())
    logger.info("Unique AMFI codes: %d", unique_amfi_codes)

    # --- NAV range ------------------------------------------------------ #
    # Coerce to numeric so any stray non-numeric values do not break min/max.
    nav_numeric = pd.to_numeric(df["nav"], errors="coerce")
    min_nav = nav_numeric.min()
    max_nav = nav_numeric.max()
    logger.info("Minimum NAV: %s", min_nav)
    logger.info("Maximum NAV: %s", max_nav)

    # --- Date range ----------------------------------------------------- #
    # Coerce to datetime so unparseable dates become NaT rather than errors.
    date_parsed = pd.to_datetime(df["date"], errors="coerce")
    earliest_date = date_parsed.min()
    latest_date = date_parsed.max()
    logger.info("Earliest date: %s", earliest_date)
    logger.info("Latest date: %s", latest_date)

    # Assemble the summary as metric/value pairs for a tidy CSV output.
    summary = {
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "duplicate_rows": duplicate_rows,
        "unique_amfi_codes": unique_amfi_codes,
        "missing_amfi_code": int(missing_per_column.get("amfi_code", 0)),
        "missing_date": int(missing_per_column.get("date", 0)),
        "missing_nav": int(missing_per_column.get("nav", 0)),
        "min_nav": min_nav,
        "max_nav": max_nav,
        "earliest_date": earliest_date,
        "latest_date": latest_date,
    }
    return summary


def save_summary(summary: dict, path: Path) -> None:
    """Persist the profiling summary as a two-column (metric, value) CSV."""
    # Ensure the output directory exists.
    path.parent.mkdir(parents=True, exist_ok=True)

    summary_df = pd.DataFrame(
        {"metric": list(summary.keys()), "value": list(summary.values())}
    )
    summary_df.to_csv(path, index=False)
    logger.info("Profiling summary saved to %s", path)


def main() -> None:
    """Entry point: load, describe, profile, and save the summary."""
    df = load_dataset(RAW_PATH)
    describe_structure(df)
    summary = profile_dataset(df)
    save_summary(summary, OUTPUT_PATH)
    logger.info("Profiling complete.")


if __name__ == "__main__":
    main()
