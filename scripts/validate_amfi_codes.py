"""Validate AMFI code consistency between the fund master and NAV history datasets.

For the Bluestock Mutual Fund Analytics Capstone, this script cross-checks the
``amfi_code`` keys shared by the fund master and the NAV history files, reports
any mismatches, and persists a per-code validation report.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
FUND_MASTER_PATH = Path("data/raw/01_fund_master.csv")
NAV_HISTORY_PATH = Path("data/raw/02_nav_history.csv")
REPORT_PATH = Path("data/processed/amfi_validation_report.csv")
KEY_COLUMN = "amfi_code"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("validate_amfi_codes")


def load_dataset(path: Path, key_column: str) -> pd.DataFrame:
    """Load a CSV dataset and confirm the key column is present."""
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info("Loading dataset: %s", path)
    df = pd.read_csv(path)

    if key_column not in df.columns:
        raise KeyError(f"Column '{key_column}' missing from {path}")

    logger.info("Loaded %s rows from %s", f"{len(df):,}", path.name)
    return df


def extract_codes(df: pd.DataFrame, key_column: str) -> set[int]:
    """Return the set of unique, non-null key values from a dataframe."""
    codes = df[key_column].dropna().unique()
    return set(codes.tolist())


def build_report(
    master_codes: set, nav_codes: set, key_column: str
) -> pd.DataFrame:
    """Build a per-code validation report across both datasets."""
    all_codes = sorted(master_codes | nav_codes)
    records = []
    for code in all_codes:
        in_master = code in master_codes
        in_nav = code in nav_codes
        if in_master and in_nav:
            status = "MATCHED"
        elif in_master:
            status = "MISSING_IN_NAV_HISTORY"
        else:
            status = "MISSING_IN_FUND_MASTER"
        records.append(
            {
                key_column: code,
                "in_fund_master": in_master,
                "in_nav_history": in_nav,
                "status": status,
            }
        )
    return pd.DataFrame.from_records(records)


def main() -> int:
    try:
        master_df = load_dataset(FUND_MASTER_PATH, KEY_COLUMN)
        nav_df = load_dataset(NAV_HISTORY_PATH, KEY_COLUMN)

        master_codes = extract_codes(master_df, KEY_COLUMN)
        nav_codes = extract_codes(nav_df, KEY_COLUMN)

        missing_in_nav = master_codes - nav_codes
        missing_in_master = nav_codes - master_codes
        matching = master_codes & nav_codes
        total_missing = len(missing_in_nav) + len(missing_in_master)

        logger.info("Total codes in fund_master : %s", f"{len(master_codes):,}")
        logger.info("Total codes in nav_history : %s", f"{len(nav_codes):,}")
        logger.info("Matching codes             : %s", f"{len(matching):,}")
        logger.info("Missing codes              : %s", f"{total_missing:,}")
        logger.info("  - in fund_master, not in nav_history: %s", f"{len(missing_in_nav):,}")
        logger.info("  - in nav_history, not in fund_master: %s", f"{len(missing_in_master):,}")

        report_df = build_report(master_codes, nav_codes, KEY_COLUMN)

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(REPORT_PATH, index=False)
        logger.info("Validation report saved to: %s", REPORT_PATH)

        print("\n" + "=" * 60)
        print("DATA QUALITY SUMMARY — AMFI CODE VALIDATION")
        print("=" * 60)
        print(f"Fund master codes      : {len(master_codes):,}")
        print(f"NAV history codes      : {len(nav_codes):,}")
        print(f"Matching codes         : {len(matching):,}")
        print(f"Missing codes (total)  : {total_missing:,}")
        print(f"  Missing in NAV       : {len(missing_in_nav):,}")
        print(f"  Missing in master    : {len(missing_in_master):,}")
        coverage = (len(matching) / len(master_codes) * 100) if master_codes else 0.0
        print(f"Master->NAV coverage   : {coverage:.2f}%")
        verdict = "PASS" if total_missing == 0 else "REVIEW REQUIRED"
        print(f"Overall status         : {verdict}")
        print("=" * 60)

        return 0

    except (FileNotFoundError, KeyError) as exc:
        logger.error("Validation failed: %s", exc)
        return 1
    except pd.errors.EmptyDataError as exc:
        logger.error("Encountered an empty dataset: %s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.exception("Unexpected error during validation: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
