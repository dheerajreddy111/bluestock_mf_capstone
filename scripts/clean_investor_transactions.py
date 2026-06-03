"""
clean_investor_transactions.py
Bluestock Mutual Fund Analytics Capstone - Day 2

Cleans the raw investor transactions dataset:
  - standardizes transaction_type values (SIP / Lumpsum / Redemption)
  - validates amount, transaction_type, investor_id, transaction_date, kyc_status
  - removes duplicate rows
  - writes a cleaned dataset and a data-quality report

Outputs:
  data/processed/clean_investor_transactions.csv
  data/processed/investor_transaction_quality_report.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_PATH = Path("data/raw/08_investor_transactions.csv")
CLEAN_PATH = Path("data/processed/clean_investor_transactions.csv")
REPORT_PATH = Path("data/processed/investor_transaction_quality_report.csv")

# The column that holds the transaction amount in this dataset.
AMOUNT_COLUMN = "amount_inr"

# Columns we must have to clean the data at all.
REQUIRED_COLUMNS = [
    "investor_id",
    "transaction_date",
    "transaction_type",
    AMOUNT_COLUMN,
    "kyc_status",
]

# The only transaction types we accept (after standardizing).
VALID_TRANSACTION_TYPES = ["SIP", "Lumpsum", "Redemption"]

# The only KYC statuses we accept.
VALID_KYC_STATUSES = ["Verified", "Pending", "Rejected"]

# Map many possible raw spellings to the clean transaction type.
# Keys are lower-cased so matching is case-insensitive.
TRANSACTION_TYPE_MAP = {
    "sip": "SIP",
    "s.i.p": "SIP",
    "systematic investment plan": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "lump-sum": "Lumpsum",
    "one time": "Lumpsum",
    "onetime": "Lumpsum",
    "redemption": "Redemption",
    "redeem": "Redemption",
    "withdrawal": "Redemption",
}

# Map possible raw KYC spellings to the clean status.
KYC_STATUS_MAP = {
    "verified": "Verified",
    "verify": "Verified",
    "approved": "Verified",
    "pending": "Pending",
    "in progress": "Pending",
    "rejected": "Rejected",
    "reject": "Rejected",
    "failed": "Rejected",
}

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
    """Load the raw investor transactions dataset from a CSV file."""
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


def standardize_category(series: pd.Series, mapping: dict) -> pd.Series:
    """
    Clean up a text column:
      - strip extra spaces
      - match known spellings (case-insensitive) to a standard value
      - leave anything unknown untouched so validation can flag it
    """
    # Convert to string, trim whitespace, and collapse to lower case for lookup.
    cleaned = series.astype(str).str.strip()
    lookup = cleaned.str.lower()

    # Replace known spellings; keep the original cleaned text if not in the map.
    return lookup.map(mapping).fillna(cleaned)


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the dataset and collect counts for the quality report.

    Returns the cleaned DataFrame and a dictionary of statistics.
    """
    # Remember how many rows we started with.
    original_rows = len(df)

    # --- 1. Count missing values up front (across the whole dataset) ------
    missing_values = int(df.isna().sum().sum())

    # --- 2. Convert data types --------------------------------------------
    # Convert transaction_date to real datetime; bad values become NaT.
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

    # Convert the amount to a number; anything non-numeric becomes NaN.
    df[AMOUNT_COLUMN] = pd.to_numeric(df[AMOUNT_COLUMN], errors="coerce")

    # --- 3. Standardize text categories -----------------------------------
    df["transaction_type"] = standardize_category(
        df["transaction_type"], TRANSACTION_TYPE_MAP
    )
    df["kyc_status"] = standardize_category(df["kyc_status"], KYC_STATUS_MAP)

    # --- 4. Remove duplicate rows -----------------------------------------
    before_dupes = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before_dupes - len(df)
    logger.info("Removed %d duplicate rows", duplicates_removed)

    # --- 5. Build validation masks (True = the row FAILS this check) -------
    # Amount must be present and strictly greater than 0.
    invalid_amount_mask = df[AMOUNT_COLUMN].isna() | (df[AMOUNT_COLUMN] <= 0)

    # Transaction type must be one of the accepted values.
    invalid_type_mask = ~df["transaction_type"].isin(VALID_TRANSACTION_TYPES)

    # KYC status must be one of the accepted values.
    invalid_kyc_mask = ~df["kyc_status"].isin(VALID_KYC_STATUSES)

    # investor_id must not be null.
    invalid_investor_mask = df["investor_id"].isna()

    # transaction_date must have parsed correctly.
    invalid_date_mask = df["transaction_date"].isna()

    # Count each kind of problem for the quality report.
    invalid_amounts = int(invalid_amount_mask.sum())
    invalid_transaction_types = int(invalid_type_mask.sum())
    invalid_kyc_statuses = int(invalid_kyc_mask.sum())
    logger.info(
        "Invalid -> amounts: %d, types: %d, kyc: %d, investor_id: %d, dates: %d",
        invalid_amounts,
        invalid_transaction_types,
        invalid_kyc_statuses,
        int(invalid_investor_mask.sum()),
        int(invalid_date_mask.sum()),
    )

    # --- 6. Keep only rows that pass every check --------------------------
    bad_row_mask = (
        invalid_amount_mask
        | invalid_type_mask
        | invalid_kyc_mask
        | invalid_investor_mask
        | invalid_date_mask
    )
    cleaned = df[~bad_row_mask].copy()

    # Make sure the amount is stored as a float in the final output.
    cleaned[AMOUNT_COLUMN] = cleaned[AMOUNT_COLUMN].astype(float)

    # Sort for a tidy, predictable output.
    cleaned = cleaned.sort_values(
        ["transaction_date", "investor_id"]
    ).reset_index(drop=True)

    # --- 7. Assemble the statistics dictionary ----------------------------
    stats = {
        "original_rows": original_rows,
        "duplicates_removed": duplicates_removed,
        "invalid_amounts": invalid_amounts,
        "invalid_transaction_types": invalid_transaction_types,
        "invalid_kyc_statuses": invalid_kyc_statuses,
        "missing_values": missing_values,
        "cleaned_rows": len(cleaned),
    }

    return cleaned, stats


def save_outputs(cleaned: pd.DataFrame, stats: dict) -> None:
    """Write the cleaned dataset and the quality report to disk."""
    # Make sure the output folder exists before writing.
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save the cleaned transactions.
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
    print("\n" + "=" * 55)
    print("INVESTOR TRANSACTIONS CLEANING SUMMARY")
    print("=" * 55)
    print(f"Original rows               : {stats['original_rows']:,}")
    print(f"Duplicates removed          : {stats['duplicates_removed']:,}")
    print(f"Invalid amounts             : {stats['invalid_amounts']:,}")
    print(f"Invalid transaction types   : {stats['invalid_transaction_types']:,}")
    print(f"Invalid KYC statuses        : {stats['invalid_kyc_statuses']:,}")
    print(f"Missing values (raw)        : {stats['missing_values']:,}")
    print(f"Cleaned rows                : {stats['cleaned_rows']:,}")
    print("=" * 55)


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
