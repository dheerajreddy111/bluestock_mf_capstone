"""
data_ingestion.py
=================

Bluestock Mutual Fund Analytics Capstone — Data Ingestion Script.

What this script does (in plain English):
1. Finds every CSV file inside the `data/raw` folder.
2. Loads each CSV into a pandas DataFrame.
3. Prints a small "report card" for each file: shape, columns, dtypes,
   the first 5 rows, and how many missing values each file has.
4. Collects a summary row for every file (name, rows, columns, missing).
5. Saves that summary to `data/processed/ingestion_summary.csv`.

The code is written to be beginner friendly: lots of comments, simple
functions, and clear logging so you can see exactly what is happening.

Run it from anywhere, for example:
    python scripts/data_ingestion.py
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
import logging                 # for nice, timestamped status messages
from pathlib import Path       # modern, OS-independent file paths

import pandas as pd            # the data analysis library we rely on


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
# `__file__` is the path to THIS script (scripts/data_ingestion.py).
# `.resolve()` makes it an absolute path, and `.parent.parent` walks up
# two folders: scripts/ -> project root (bluestock_mf_capstone/).
# Deriving paths this way means the script works no matter which folder
# you run it from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"             # where the CSVs live
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"  # where output goes
SUMMARY_FILE = PROCESSED_DIR / "ingestion_summary.csv"


# ----------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------
# logging is like print(), but better: it adds timestamps and levels
# (INFO, WARNING, ERROR) so you can tell normal messages from problems.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("data_ingestion")


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def find_csv_files(folder: Path) -> list[Path]:
    """Return a sorted list of all .csv files inside `folder`.

    Sorting keeps the output in a predictable order (01_, 02_, 03_, ...).
    """
    # `glob("*.csv")` finds every file ending in .csv in the folder.
    csv_files = sorted(folder.glob("*.csv"))
    return csv_files


def inspect_dataframe(file_name: str, df: pd.DataFrame) -> None:
    """Print a detailed "report card" for a single loaded DataFrame."""
    # A visual separator so each file's report is easy to read.
    print("\n" + "=" * 70)
    print(f"FILE: {file_name}")
    print("=" * 70)

    # Shape is a tuple: (number_of_rows, number_of_columns).
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Column names as a simple list.
    print("\nColumn names:")
    print(list(df.columns))

    # Data type of each column (int, float, object/text, etc.).
    print("\nData types:")
    print(df.dtypes)

    # The first 5 rows give a quick feel for the actual values.
    print("\nFirst 5 rows:")
    print(df.head())

    # Count of missing (NaN) values per column. 0 means no gaps.
    print("\nMissing values per column:")
    print(df.isnull().sum())


def load_and_summarize(csv_path: Path) -> dict | None:
    """Load one CSV, print its report card, and return a summary dict.

    Returns None if the file could not be read, so the caller can skip it
    without crashing the whole script.
    """
    file_name = csv_path.name  # just the file name, e.g. "01_fund_master.csv"

    try:
        logger.info("Loading %s ...", file_name)
        df = pd.read_csv(csv_path)

        # Print the detailed inspection for this file.
        inspect_dataframe(file_name, df)

        # Build one summary row describing this file.
        summary = {
            "file_name": file_name,
            "rows": df.shape[0],
            "columns": df.shape[1],
            # Total missing values across ALL columns (a single number).
            "missing_values": int(df.isnull().sum().sum()),
        }

        logger.info(
            "Loaded %s successfully (%d rows, %d cols, %d missing).",
            file_name, summary["rows"], summary["columns"],
            summary["missing_values"],
        )
        return summary

    except pd.errors.EmptyDataError:
        # The file exists but has no data / no columns.
        logger.error("%s is empty — skipping.", file_name)
        return None

    except Exception as error:
        # Catch-all so one bad file never stops the rest from loading.
        logger.error("Could not read %s: %s", file_name, error)
        return None


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------
def main() -> None:
    """Run the full ingestion process from start to finish."""
    logger.info("Starting data ingestion.")
    logger.info("Looking for CSV files in: %s", RAW_DIR)

    # Safety check: make sure the raw data folder actually exists.
    if not RAW_DIR.exists():
        logger.error("Raw data folder not found: %s", RAW_DIR)
        return

    # Step 1: discover all CSV files.
    csv_files = find_csv_files(RAW_DIR)
    if not csv_files:
        logger.warning("No CSV files found in %s. Nothing to do.", RAW_DIR)
        return
    logger.info("Found %d CSV file(s).", len(csv_files))

    # Step 2: load + inspect each file, collecting summary rows.
    summaries = []
    for csv_path in csv_files:
        summary = load_and_summarize(csv_path)
        if summary is not None:          # skip files that failed to load
            summaries.append(summary)

    # If every file failed, there is nothing to save.
    if not summaries:
        logger.error("No files were loaded successfully. No summary saved.")
        return

    # Step 3: turn the collected rows into a summary DataFrame.
    summary_df = pd.DataFrame(
        summaries,
        columns=["file_name", "rows", "columns", "missing_values"],
    )

    print("\n" + "=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)
    print(summary_df.to_string(index=False))

    # Step 4: save the summary to data/processed/ingestion_summary.csv.
    try:
        # `mkdir` with parents=True creates the folder (and any parents)
        # if it does not already exist. exist_ok=True avoids an error if
        # the folder is already there.
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(SUMMARY_FILE, index=False)
        logger.info("Summary saved to: %s", SUMMARY_FILE)
    except Exception as error:
        logger.error("Failed to save summary: %s", error)

    logger.info("Data ingestion complete.")


# This standard Python guard means main() only runs when you execute the
# file directly (python scripts/data_ingestion.py), not when it is imported.
if __name__ == "__main__":
    main()
