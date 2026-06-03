"""
check_nav_date_gaps.py
Bluestock Mutual Fund Analytics Capstone - Day 2

For each scheme (amfi_code) in the NAV history dataset, build the complete
daily calendar between the scheme's first and last observed dates, then count
how many of those calendar days are missing from the actual data.

Outputs a per-scheme gap report and prints a summary.
"""

import logging
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_PATH = Path("data/raw/02_nav_history.csv")
OUTPUT_PATH = Path("data/processed/nav_date_gap_report.csv")

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
    """Load the NAV history dataset and parse the date column."""
    logger.info("Loading dataset from %s", path)
    df = pd.read_csv(path)

    # Convert the date column to datetime so we can do date arithmetic.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop any rows where the date failed to parse - they can't be analysed.
    bad_dates = df["date"].isna().sum()
    if bad_dates:
        logger.warning("Dropping %d rows with unparseable dates", bad_dates)
        df = df.dropna(subset=["date"])

    logger.info("Loaded %d rows across %d schemes", len(df), df["amfi_code"].nunique())
    return df


def compute_date_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each amfi_code, compare the actual dates against the complete daily
    calendar between its min and max date, and count the missing days.
    """
    records = []

    # Process one scheme at a time.
    for amfi_code, group in df.groupby("amfi_code"):
        # Sort by date and keep only the unique calendar days present.
        actual_dates = group.sort_values("date")["date"].dt.normalize().drop_duplicates()

        start_date = actual_dates.min()
        end_date = actual_dates.max()

        # Build the complete daily date range (inclusive of both endpoints).
        expected_dates = pd.date_range(start=start_date, end=end_date, freq="D")

        # Missing dates = expected calendar days not present in the actual data.
        missing_dates = expected_dates.difference(actual_dates)

        records.append(
            {
                "amfi_code": amfi_code,
                "start_date": start_date.date(),
                "end_date": end_date.date(),
                "expected_days": len(expected_dates),
                "actual_days": len(actual_dates),
                "missing_days": len(missing_dates),
            }
        )

    report = pd.DataFrame(records)
    # Sort so the worst offenders appear first.
    report = report.sort_values("missing_days", ascending=False).reset_index(drop=True)
    return report


def main() -> None:
    # 1-2. Load data and convert the date column.
    df = load_data(RAW_PATH)

    # 3-4. Build per-scheme gap report.
    report = compute_date_gaps(df)

    # 5. Save the report, creating the output directory if needed.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_PATH, index=False)
    logger.info("Gap report written to %s", OUTPUT_PATH)

    # 6. Print the top 10 schemes with the most missing dates.
    total_missing = int(report["missing_days"].sum())
    logger.info("Top 10 schemes with the most missing dates:")
    print("\nTop 10 schemes by missing dates")
    print("-" * 60)
    print(report.head(10).to_string(index=False))

    print("-" * 60)
    print(f"Total missing dates across all schemes: {total_missing:,}")


if __name__ == "__main__":
    main()
