"""
clean_nav_history.py
Bluestock Mutual Fund Analytics Capstone - Day 2

Cleans the raw NAV history dataset:
  - validates and fixes data types
  - removes duplicates and invalid NAV rows
  - fills weekend/holiday gaps via forward-fill (NAVs exist only on trading days)
  - writes a cleaned dataset and a data-quality report

Outputs:
  data/processed/clean_nav_history.csv
  data/processed/nav_quality_report.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_PATH = Path("data/raw/02_nav_history.csv")
CLEAN_PATH = Path("data/processed/clean_nav_history.csv")
REPORT_PATH = Path("data/processed/nav_quality_report.csv")

# The columns we expect the raw file to contain.
REQUIRED_COLUMNS = ["amfi_code", "date", "nav"]

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_data(path: Path) -> pd.DataFrame:
    """Load the raw NAV history dataset from a CSV file."""
    logger.info("Loading raw dataset from %s", path)
    if not path.exists():
        # If the file is missing there is nothing to clean - stop early.
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path)
    logger.info("Loaded %d rows and %d columns", len(df), df.shape[1])
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """Make sure every required column is present before we continue."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        # Without these columns the rest of the script cannot run.
        raise ValueError(f"Missing required columns: {missing}")
    logger.info("Column check passed: %s", REQUIRED_COLUMNS)


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the dataset and collect counts for the quality report.

    Returns the cleaned DataFrame and a dictionary of statistics.
    """
    # Keep track of how many rows we started with.
    original_rows = len(df)

    # --- 1. Convert data types --------------------------------------------
    # Convert the date column to real datetime values; bad values become NaT.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Convert nav to a number; anything non-numeric becomes NaN.
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # --- 2. Validate / drop invalid rows ----------------------------------
    # A row is valid only if:
    #   - amfi_code is present (not null)
    #   - date parsed correctly (not NaT)
    #   - nav parsed correctly (not NaN)
    #   - nav is strictly greater than 0
    valid_mask = (
        df["amfi_code"].notna()
        & df["date"].notna()
        & df["nav"].notna()
        & (df["nav"] > 0)
    )

    # Rows that fail any of the above checks are considered invalid.
    invalid_rows_removed = int((~valid_mask).sum())
    df = df[valid_mask].copy()
    logger.info("Removed %d invalid rows", invalid_rows_removed)

    # Ensure nav is stored as float.
    df["nav"] = df["nav"].astype(float)

    # --- 3. Remove duplicate rows -----------------------------------------
    before_dupes = len(df)
    df = df.drop_duplicates()
    duplicate_rows_removed = before_dupes - len(df)
    logger.info("Removed %d duplicate rows", duplicate_rows_removed)

    # --- 4. Sort the data -------------------------------------------------
    # Sort by scheme first, then by date, so each scheme is in time order.
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Row count after validation/dedup but before forward-filling gaps.
    rows_before_fill = len(df)

    # --- 5. Forward-fill weekend/holiday gaps per scheme ------------------
    filled_frames = []
    for amfi_code, group in df.groupby("amfi_code"):
        # Keep one NAV per calendar day (defensive: drop same-day duplicates).
        group = group.drop_duplicates(subset="date").set_index("date").sort_index()

        # Build the full daily calendar between the first and last date.
        full_range = pd.date_range(start=group.index.min(),
                                   end=group.index.max(),
                                   freq="D")

        # Reindex onto the full calendar; new (missing) days get NaN...
        group = group.reindex(full_range)

        # ...then forward-fill so weekends/holidays inherit the last NAV.
        group["nav"] = group["nav"].ffill()

        # The amfi_code is constant for this group; refill it for new rows.
        group["amfi_code"] = amfi_code

        # Restore the date as a normal column named "date".
        group = group.rename_axis("date").reset_index()
        filled_frames.append(group)

    # Combine all schemes back into one DataFrame.
    cleaned = pd.concat(filled_frames, ignore_index=True)

    # Put columns back in a tidy, predictable order.
    cleaned = cleaned[["amfi_code", "date", "nav"]]
    cleaned = cleaned.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # How many brand-new dates did forward-fill add?
    dates_added = len(cleaned) - rows_before_fill

    # --- 6. Assemble the statistics dictionary ----------------------------
    stats = {
        "original_row_count": original_rows,
        "cleaned_row_count": len(cleaned),
        "duplicate_rows_removed": duplicate_rows_removed,
        "invalid_nav_rows_removed": invalid_rows_removed,
        "dates_added_forward_fill": dates_added,
    }

    return cleaned, stats


def save_outputs(cleaned: pd.DataFrame, stats: dict) -> None:
    """Write the cleaned dataset and the quality report to disk."""
    # Make sure the output folder exists before writing.
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save the cleaned NAV history.
    cleaned.to_csv(CLEAN_PATH, index=False)
    logger.info("Cleaned dataset written to %s", CLEAN_PATH)

    # Save the quality report as a two-column (metric, value) table.
    report = pd.DataFrame(
        [{"metric": key, "value": value} for key, value in stats.items()]
    )
    report.to_csv(REPORT_PATH, index=False)
    logger.info("Quality report written to %s", REPORT_PATH)


def print_summary(stats: dict) -> None:
    """Print a friendly final summary of what the cleaning step did."""
    print("\n" + "=" * 50)
    print("NAV HISTORY CLEANING SUMMARY")
    print("=" * 50)
    print(f"Original rows            : {stats['original_row_count']:,}")
    print(f"Invalid NAV rows removed : {stats['invalid_nav_rows_removed']:,}")
    print(f"Duplicate rows removed   : {stats['duplicate_rows_removed']:,}")
    print(f"Dates added (fwd fill)   : {stats['dates_added_forward_fill']:,}")
    print(f"Cleaned rows             : {stats['cleaned_row_count']:,}")
    print("=" * 50)


def main() -> None:
    """Run the full cleaning pipeline with top-level error handling."""
    try:
        # 1. Load the raw data.
        df = load_data(RAW_PATH)

        # 2. Make sure the required columns are present.
        validate_columns(df)

        # 3. Clean the data and gather statistics.
        cleaned, stats = clean_data(df)

        # 4. Save the cleaned data and the quality report.
        save_outputs(cleaned, stats)

        # 5. Print a final summary for the user.
        print_summary(stats)

    except Exception as error:
        # Log any unexpected problem and exit with a non-zero status code.
        logger.exception("Cleaning failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
