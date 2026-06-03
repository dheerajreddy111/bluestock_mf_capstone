-- =============================================================================
-- schema.sql
-- Bluestock Mutual Fund Analytics Capstone - Day 2
-- SQLite star schema for the Mutual Fund Analytics platform.
--
-- Design: classic star schema.
--   * Dimensions describe the "who / what / when" (dim_fund, dim_date).
--   * Facts hold the measurable events/metrics and point back to dimensions
--     via foreign keys.
--
-- Supports: NAV trend analysis, performance metrics, transaction analysis,
--           AUM analysis, and dashboard reporting.
--
-- Enforce foreign keys in SQLite (off by default):
--   PRAGMA foreign_keys = ON;
-- =============================================================================

PRAGMA foreign_keys = ON;


-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- dim_fund
-- One row per mutual fund scheme (sourced from fund_master).
-- This is the central scheme dimension that NAV, transaction and performance
-- facts all join to. The natural key is the AMFI code.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_fund (
    amfi_code           INTEGER PRIMARY KEY,   -- AMFI scheme code (natural key)
    fund_house          TEXT    NOT NULL,      -- AMC / fund house name
    scheme_name         TEXT    NOT NULL,      -- full scheme name
    category            TEXT,                  -- e.g. Equity, Debt
    sub_category        TEXT,                  -- e.g. Large Cap, Gilt
    plan                TEXT,                  -- Regular / Direct
    launch_date         TEXT,                  -- ISO date 'YYYY-MM-DD'
    benchmark           TEXT,                  -- benchmark index name
    expense_ratio_pct   REAL,                  -- current expense ratio (%)
    exit_load_pct       REAL,                  -- exit load (%)
    min_sip_amount      REAL,                  -- minimum SIP amount (INR)
    min_lumpsum_amount  REAL,                  -- minimum lumpsum amount (INR)
    fund_manager        TEXT,                  -- primary fund manager
    risk_category       TEXT,                  -- e.g. Moderate, High
    sebi_category_code  TEXT                   -- SEBI category code
);

-- Lookups by fund house / category are common in dashboards.
CREATE INDEX idx_dim_fund_fund_house ON dim_fund (fund_house);
CREATE INDEX idx_dim_fund_category   ON dim_fund (category);


-- -----------------------------------------------------------------------------
-- dim_date
-- One row per calendar day. A shared date dimension lets every fact be sliced
-- by year / quarter / month / weekday consistently. The key is an integer in
-- YYYYMMDD form (e.g. 20240131) which is compact and naturally sortable.
-- -----------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,   -- YYYYMMDD (e.g. 20240131)
    full_date     TEXT    NOT NULL UNIQUE,-- ISO date 'YYYY-MM-DD'
    year          INTEGER NOT NULL,      -- 2024
    quarter       INTEGER NOT NULL,      -- 1..4
    month         INTEGER NOT NULL,      -- 1..12
    month_name    TEXT,                  -- 'January'
    day           INTEGER NOT NULL,      -- 1..31
    day_of_week   INTEGER,               -- 0=Mon .. 6=Sun
    day_name      TEXT,                  -- 'Monday'
    is_weekend    INTEGER NOT NULL DEFAULT 0,  -- 0/1 flag
    is_month_end  INTEGER NOT NULL DEFAULT 0   -- 0/1 flag (useful for AUM)
);

-- Frequent filtering on year/month for trend charts.
CREATE INDEX idx_dim_date_year_month ON dim_date (year, month);


-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- fact_nav
-- Daily NAV per scheme (sourced from clean_nav_history).
-- Grain: one row per (scheme, day). Powers NAV trend analysis and returns.
-- -----------------------------------------------------------------------------
CREATE TABLE fact_nav (
    nav_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code  INTEGER NOT NULL,   -- FK -> dim_fund
    date_key   INTEGER NOT NULL,   -- FK -> dim_date
    nav        REAL    NOT NULL,   -- net asset value (INR)

    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date_key)  REFERENCES dim_date (date_key),

    -- One NAV per scheme per day.
    UNIQUE (amfi_code, date_key)
);

-- Index to pull a scheme's NAV series in date order (trend charts).
CREATE INDEX idx_fact_nav_fund_date ON fact_nav (amfi_code, date_key);
CREATE INDEX idx_fact_nav_date      ON fact_nav (date_key);


-- -----------------------------------------------------------------------------
-- fact_transactions
-- Investor transactions (sourced from clean_investor_transactions).
-- Grain: one row per investor transaction. Powers transaction analysis
-- (SIP vs Lumpsum vs Redemption, inflow/outflow, demographics).
-- Investor demographics are kept inline here (degenerate / mini-dimension)
-- to keep the model simple for the capstone.
-- -----------------------------------------------------------------------------
CREATE TABLE fact_transactions (
    transaction_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT    NOT NULL,   -- investor identifier
    amfi_code          INTEGER NOT NULL,   -- FK -> dim_fund
    date_key           INTEGER NOT NULL,   -- FK -> dim_date (transaction date)
    transaction_type   TEXT    NOT NULL,   -- SIP / Lumpsum / Redemption
    amount_inr         REAL    NOT NULL,   -- transaction amount (INR)

    -- Investor demographic attributes (descriptive context).
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,               -- T30 / B30
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,               -- UPI / Cheque / Mandate ...
    kyc_status         TEXT,               -- Verified / Pending / Rejected

    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date_key)  REFERENCES dim_date (date_key)
);

-- Common slices: by fund, by date, by type, by investor.
CREATE INDEX idx_fact_txn_fund      ON fact_transactions (amfi_code);
CREATE INDEX idx_fact_txn_date      ON fact_transactions (date_key);
CREATE INDEX idx_fact_txn_type      ON fact_transactions (transaction_type);
CREATE INDEX idx_fact_txn_investor  ON fact_transactions (investor_id);


-- -----------------------------------------------------------------------------
-- fact_performance
-- Point-in-time performance & risk metrics per scheme
-- (sourced from clean_scheme_performance).
-- Grain: one row per scheme (a snapshot). Powers performance dashboards,
-- risk-adjusted return comparisons and ratings.
-- -----------------------------------------------------------------------------
CREATE TABLE fact_performance (
    performance_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,  -- FK -> dim_fund
    date_key            INTEGER,           -- FK -> dim_date (snapshot date, optional)

    -- Return measures (%).
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,

    -- Risk / risk-adjusted measures.
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,

    -- Size & ratings.
    aum_crore           REAL,              -- scheme AUM (INR crore)
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,           -- 1..5
    risk_grade          TEXT,              -- Low / Moderate / High / Very High

    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date_key)  REFERENCES dim_date (date_key),

    -- One performance snapshot per scheme per date.
    UNIQUE (amfi_code, date_key)
);

CREATE INDEX idx_fact_perf_fund   ON fact_performance (amfi_code);
CREATE INDEX idx_fact_perf_rating ON fact_performance (morningstar_rating);


-- -----------------------------------------------------------------------------
-- fact_aum
-- Assets Under Management by fund house over time
-- (sourced from aum_by_fund_house).
-- Grain: one row per (fund_house, date). Note this fact is at FUND-HOUSE level,
-- not scheme level, so it joins to dim_fund by fund_house (not amfi_code).
-- Powers AUM analysis and fund-house market-share dashboards.
-- -----------------------------------------------------------------------------
CREATE TABLE fact_aum (
    aum_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house       TEXT    NOT NULL,   -- AMC name (links to dim_fund.fund_house)
    date_key         INTEGER NOT NULL,   -- FK -> dim_date
    aum_lakh_crore   REAL,               -- AUM in lakh crore
    aum_crore        REAL,               -- AUM in crore
    num_schemes      INTEGER,            -- number of schemes run by the AMC

    FOREIGN KEY (date_key) REFERENCES dim_date (date_key),

    -- One AUM record per fund house per date.
    UNIQUE (fund_house, date_key)
);

CREATE INDEX idx_fact_aum_fund_house ON fact_aum (fund_house);
CREATE INDEX idx_fact_aum_date       ON fact_aum (date_key);


-- =============================================================================
-- OPTIONAL: benchmark_indices
-- Daily benchmark index close values (sourced from benchmark_indices).
-- Not a core star fact, but useful for comparing scheme NAV/returns against
-- market benchmarks in dashboards.
-- Grain: one row per (index, day).
-- =============================================================================
CREATE TABLE fact_benchmark (
    benchmark_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name    TEXT    NOT NULL,   -- e.g. 'NIFTY50'
    date_key      INTEGER NOT NULL,   -- FK -> dim_date
    close_value   REAL    NOT NULL,   -- index close value

    FOREIGN KEY (date_key) REFERENCES dim_date (date_key),

    UNIQUE (index_name, date_key)
);

CREATE INDEX idx_fact_benchmark_index_date ON fact_benchmark (index_name, date_key);
