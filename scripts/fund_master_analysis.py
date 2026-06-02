"""
fund_master_analysis.py
=======================

Bluestock Mutual Fund Analytics Capstone — Fund Master Analysis.

What this script does (in plain English):
1. Loads the fund master dataset (data/raw/01_fund_master.csv).
2. Prints key facts: total schemes, fund houses, categories,
   sub-categories, and risk categories.
3. Builds three summary tables:
     - how many schemes each fund house has
     - how many schemes each category has
     - how many schemes each risk category has
4. Saves those tables to an Excel file with one sheet each:
     data/processed/fund_master_summary.xlsx

The code is beginner friendly: small functions, plenty of comments, and
clear logging so you can follow exactly what happens.

Run it, for example:
    python scripts/fund_master_analysis.py
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
import logging                 # timestamped status messages
from pathlib import Path       # OS-independent file paths

import pandas as pd            # the data analysis library


# ----------------------------------------------------------------------
# Configuration (file paths)
# ----------------------------------------------------------------------
# `__file__` is this script. `.resolve().parent.parent` walks up from
# scripts/ to the project root, so paths work from any folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "01_fund_master.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "fund_master_summary.xlsx"


# ----------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fund_master_analysis")


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load the fund master CSV into a pandas DataFrame.

    Raises an exception if the file is missing or unreadable; the caller
    handles that so the program can stop with a clear message.
    """
    logger.info("Loading data from %s", csv_path)
    df = pd.read_csv(csv_path)
    logger.info("Loaded %d rows and %d columns.", df.shape[0], df.shape[1])
    return df


def print_overview(df: pd.DataFrame) -> None:
    """Print the headline facts about the fund master dataset."""
    print("\n" + "=" * 60)
    print("FUND MASTER OVERVIEW")
    print("=" * 60)

    # Each scheme is one row in the dataset.
    print(f"Total number of schemes : {len(df)}")

    # `nunique()` counts how many DIFFERENT values a column has.
    print(f"Count of fund houses    : {df['fund_house'].nunique()}")

    # Show the actual unique values for the key descriptive columns.
    # `sorted()` makes the lists easy to read.
    print("\nUnique fund houses:")
    print(sorted(df["fund_house"].unique()))

    print("\nUnique categories:")
    print(sorted(df["category"].unique()))

    print("\nUnique sub-categories:")
    print(sorted(df["sub_category"].unique()))

    print("\nUnique risk categories:")
    print(sorted(df["risk_category"].unique()))


def schemes_per(df: pd.DataFrame, column: str, count_label: str) -> pd.DataFrame:
    """Count how many schemes fall under each value of `column`.

    Returns a tidy two-column DataFrame, sorted from most to fewest
    schemes, ready to be written to Excel.
    """
    # `value_counts()` tallies each unique value; resetting the index
    # turns that tally into a normal two-column table.
    summary = (
        df[column]
        .value_counts()
        .reset_index()
    )
    # Give the columns friendly, self-explanatory names.
    summary.columns = [column, count_label]
    return summary


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------
def main() -> None:
    """Run the full fund master analysis from start to finish."""
    logger.info("Starting fund master analysis.")

    # Step 1: load the data (with error handling).
    try:
        df = load_data(INPUT_FILE)
    except FileNotFoundError:
        logger.error("Input file not found: %s", INPUT_FILE)
        return
    except Exception as error:
        logger.error("Could not read %s: %s", INPUT_FILE, error)
        return

    # Step 2: print the overview facts.
    print_overview(df)

    # Step 3: build the three summary tables.
    fund_houses = schemes_per(df, "fund_house", "scheme_count")
    categories = schemes_per(df, "category", "scheme_count")
    risk_categories = schemes_per(df, "risk_category", "scheme_count")

    # Show the tables on screen too.
    print("\n" + "=" * 60)
    print("SCHEMES PER FUND HOUSE")
    print("=" * 60)
    print(fund_houses.to_string(index=False))

    print("\n" + "=" * 60)
    print("SCHEMES PER CATEGORY")
    print("=" * 60)
    print(categories.to_string(index=False))

    print("\n" + "=" * 60)
    print("SCHEMES PER RISK CATEGORY")
    print("=" * 60)
    print(risk_categories.to_string(index=False))

    # Step 4: save everything to one Excel file, one sheet per table.
    try:
        # Create data/processed/ if it does not exist yet.
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        # An ExcelWriter lets us write several sheets into one .xlsx file.
        # `openpyxl` is the engine that actually writes the file.
        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
            fund_houses.to_excel(writer, sheet_name="fund_houses", index=False)
            categories.to_excel(writer, sheet_name="categories", index=False)
            risk_categories.to_excel(
                writer, sheet_name="risk_categories", index=False
            )

        logger.info("Summary saved to: %s", OUTPUT_FILE)
    except Exception as error:
        logger.error("Failed to save Excel file: %s", error)
        return

    logger.info("Fund master analysis complete.")


# Only run main() when the file is executed directly, not when imported.
if __name__ == "__main__":
    main()
