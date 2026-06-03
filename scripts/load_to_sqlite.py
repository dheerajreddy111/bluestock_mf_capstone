"""
load_to_sqlite.py
Bluestock Mutual Fund Analytics Capstone - Day 2

Builds the SQLite analytics database from the cleaned / raw datasets:
  1. creates the database (and folder) if missing
  2. runs sql/schema.sql to create the star-schema tables
  3. builds dim_date automatically from all dated datasets
  4. loads dim_fund, then every fact table
  5. verifies row counts and writes a load summary

Database:
  data/db/bluestock_mf.db

Run:
  python load_to_sqlite.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH = Path("data/db/bluestock_mf.db")
SCHEMA_PATH = Path("sql/schema.sql")
SUMMARY_PATH = Path("data/processed/load_summary.csv")

# Input datasets (a mix of raw and cleaned files).
FUND_MASTER_PATH = Path("data/raw/01_fund_master.csv")
NAV_PATH = Path("data/processed/clean_nav_history.csv")
TRANSACTIONS_PATH = Path("data/processed/clean_investor_transactions.csv")
PERFORMANCE_PATH = Path("data/processed/clean_scheme_performance.csv")
AUM_PATH = Path("data/raw/03_aum_by_fund_house.csv")
BENCHMARK_PATH = Path("data/raw/10_benchmark_indices.csv")

# Every file we depend on - used for the "fail if missing" check.
REQUIRED_FILES = [
    SCHEMA_PATH,
    FUND_MASTER_PATH,
    NAV_PATH,
    TRANSACTIONS_PATH,
    PERFORMANCE_PATH,
    AUM_PATH,
    BENCHMARK_PATH,
]

# The tables we expect to populate, in load order.
FACT_TABLES = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_aum",
    "fact_benchmark",
]

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def check_required_files() -> None:
    """Stop early (with a clear message) if any input file is missing."""
    missing = [str(p) for p in REQUIRED_FILES if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required input file(s):\n  " + "\n  ".join(missing)
        )
    logger.info("All %d required input files found", len(REQUIRED_FILES))


def to_date_key(series: pd.Series) -> pd.Series:
    """
    Convert a column of dates into an integer date_key in YYYYMMDD form.
    Example: 2024-01-31 -> 20240131. Bad dates become NaT then are dropped
    by the caller where needed.
    """
    dates = pd.to_datetime(series, errors="coerce")
    # strftime gives a 'YYYYMMDD' string; convert to a nullable integer.
    return dates.dt.strftime("%Y%m%d").astype("Int64")


def run_schema(engine) -> None:
    """Execute sql/schema.sql to (re)create all tables."""
    logger.info("Executing schema from %s", SCHEMA_PATH)
    schema_sql = SCHEMA_PATH.read_text()

    # SQLite's DBAPI can run a whole multi-statement script at once via
    # executescript. We reach the raw connection through SQLAlchemy.
    raw_conn = engine.raw_connection()
    try:
        raw_conn.executescript(schema_sql)
        raw_conn.commit()
    finally:
        raw_conn.close()
    logger.info("Schema created successfully")


def build_dim_date(*date_series: pd.Series) -> pd.DataFrame:
    """
    Build the date dimension from every date found across the datasets.
    Accepts any number of date columns, combines them, removes duplicates,
    and derives the calendar attributes.
    """
    # Combine all incoming date columns into one long series.
    all_dates = pd.concat(
        [pd.to_datetime(s, errors="coerce") for s in date_series],
        ignore_index=True,
    )

    # Keep only valid, unique calendar days, sorted in order.
    unique_dates = pd.Series(all_dates.dropna().dt.normalize().unique())
    unique_dates = unique_dates.sort_values().reset_index(drop=True)
    unique_dates = pd.to_datetime(unique_dates)

    # Build the dimension one column at a time using pandas date helpers.
    dim = pd.DataFrame({"full_date": unique_dates})
    dim["date_key"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["full_date"].dt.year
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.month_name()
    dim["day"] = dim["full_date"].dt.day
    dim["day_of_week"] = dim["full_date"].dt.dayofweek  # 0=Mon .. 6=Sun
    dim["day_name"] = dim["full_date"].dt.day_name()
    # Saturday (5) and Sunday (6) are weekends.
    dim["is_weekend"] = (dim["day_of_week"] >= 5).astype(int)
    # is_month_end flag is handy for month-end AUM snapshots.
    dim["is_month_end"] = dim["full_date"].dt.is_month_end.astype(int)

    # Store full_date as a plain ISO string to match the schema (TEXT).
    dim["full_date"] = dim["full_date"].dt.strftime("%Y-%m-%d")

    # Put columns in the schema's order.
    dim = dim[
        [
            "date_key",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "day",
            "day_of_week",
            "day_name",
            "is_weekend",
            "is_month_end",
        ]
    ]
    logger.info("Built dim_date with %d unique dates", len(dim))
    return dim


def load_table(engine, df: pd.DataFrame, table_name: str) -> None:
    """Append a DataFrame into an existing SQLite table."""
    df.to_sql(table_name, engine, if_exists="append", index=False)
    logger.info("Loaded %d rows into %s", len(df), table_name)


def count_rows(engine, table_name: str) -> int:
    """Return the number of rows currently in a table."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return int(result.scalar_one())


# ---------------------------------------------------------------------------
# Load steps for each table
# ---------------------------------------------------------------------------
def load_dim_fund(engine) -> None:
    """Load dim_fund from the fund master file."""
    df = pd.read_csv(FUND_MASTER_PATH)

    # Keep only the columns the dim_fund table expects (in schema order).
    columns = [
        "amfi_code", "fund_house", "scheme_name", "category", "sub_category",
        "plan", "launch_date", "benchmark", "expense_ratio_pct", "exit_load_pct",
        "min_sip_amount", "min_lumpsum_amount", "fund_manager", "risk_category",
        "sebi_category_code",
    ]
    df = df[[c for c in columns if c in df.columns]]
    load_table(engine, df, "dim_fund")


def load_fact_nav(engine) -> None:
    """Load fact_nav from the cleaned NAV history."""
    df = pd.read_csv(NAV_PATH)
    df["date_key"] = to_date_key(df["date"])
    # Drop rows whose date could not be converted.
    df = df.dropna(subset=["date_key"])
    df = df[["amfi_code", "date_key", "nav"]]
    load_table(engine, df, "fact_nav")


def load_fact_transactions(engine) -> None:
    """Load fact_transactions from the cleaned investor transactions."""
    df = pd.read_csv(TRANSACTIONS_PATH)
    df["date_key"] = to_date_key(df["transaction_date"])
    df = df.dropna(subset=["date_key"])

    columns = [
        "investor_id", "amfi_code", "date_key", "transaction_type", "amount_inr",
        "state", "city", "city_tier", "age_group", "gender",
        "annual_income_lakh", "payment_mode", "kyc_status",
    ]
    df = df[[c for c in columns if c in df.columns]]
    load_table(engine, df, "fact_transactions")


def load_fact_performance(engine) -> None:
    """
    Load fact_performance from the cleaned scheme performance file.
    This dataset is a point-in-time snapshot with no date column, so date_key
    is left empty (NULL).
    """
    df = pd.read_csv(PERFORMANCE_PATH)

    # Only the measure columns defined in the schema (date_key stays NULL).
    columns = [
        "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
        "morningstar_rating", "risk_grade",
    ]
    df = df[[c for c in columns if c in df.columns]]
    load_table(engine, df, "fact_performance")


def load_fact_aum(engine) -> None:
    """Load fact_aum from the AUM-by-fund-house file."""
    df = pd.read_csv(AUM_PATH)
    df["date_key"] = to_date_key(df["date"])
    df = df.dropna(subset=["date_key"])
    df = df[["fund_house", "date_key", "aum_lakh_crore", "aum_crore", "num_schemes"]]
    load_table(engine, df, "fact_aum")


def load_fact_benchmark(engine) -> None:
    """Load fact_benchmark from the benchmark indices file."""
    df = pd.read_csv(BENCHMARK_PATH)
    df["date_key"] = to_date_key(df["date"])
    df = df.dropna(subset=["date_key"])
    df = df[["index_name", "date_key", "close_value"]]
    load_table(engine, df, "fact_benchmark")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    try:
        # 0. Fail fast if any input is missing.
        check_required_files()

        # 1. Make sure the database folder exists.
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Start from a clean database so re-running is repeatable.
        if DB_PATH.exists():
            DB_PATH.unlink()
            logger.info("Removed existing database for a fresh load")

        # 2. Connect to SQLite via SQLAlchemy.
        engine = create_engine(f"sqlite:///{DB_PATH}")

        # 3. Create all tables from schema.sql.
        run_schema(engine)

        # 4. Build dim_date from every dated dataset (NAV, txns, benchmark).
        nav_dates = pd.read_csv(NAV_PATH, usecols=["date"])["date"]
        txn_dates = pd.read_csv(TRANSACTIONS_PATH, usecols=["transaction_date"])[
            "transaction_date"
        ]
        bm_dates = pd.read_csv(BENCHMARK_PATH, usecols=["date"])["date"]
        # AUM dates included too so month-end AUM rows always find a date_key.
        aum_dates = pd.read_csv(AUM_PATH, usecols=["date"])["date"]

        dim_date = build_dim_date(nav_dates, txn_dates, bm_dates, aum_dates)
        load_table(engine, dim_date, "dim_date")

        # 5. Load the fund dimension.
        load_dim_fund(engine)

        # 6. Load all fact tables.
        load_fact_nav(engine)
        load_fact_transactions(engine)
        load_fact_performance(engine)
        load_fact_aum(engine)
        load_fact_benchmark(engine)

        # 7. Verify row counts and build a summary table.
        summary_rows = []
        print("\n" + "=" * 40)
        print("DATABASE LOAD SUMMARY")
        print("=" * 40)
        for table in FACT_TABLES:
            n = count_rows(engine, table)
            summary_rows.append({"table": table, "row_count": n})
            print(f"{table}: {n:,}")
        print("=" * 40)

        # 8. Save the load summary CSV.
        SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(summary_rows).to_csv(SUMMARY_PATH, index=False)
        logger.info("Load summary written to %s", SUMMARY_PATH)

    except Exception as error:
        # Log any unexpected problem and exit with a non-zero status code.
        logger.exception("Database load failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
