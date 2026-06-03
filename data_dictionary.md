# Data Dictionary — Bluestock Mutual Fund Analytics Capstone

**Project:** Bluestock Mutual Fund Analytics Platform
**Phase:** Day 2 — Data Cleaning, Modeling & Loading
**Database:** `data/db/bluestock_mf.db` (SQLite star schema)

This document describes every dataset used in the analytics platform: its
purpose, source, size, and the business meaning and validation rules for each
column. Datatypes are given in pandas/SQLite terms.

---

## 1. fund_master

| Field | Detail |
|---|---|
| **Purpose** | Master reference of all mutual fund schemes; the single source of truth for scheme attributes. Feeds the `dim_fund` dimension. |
| **Source** | `data/raw/01_fund_master.csv` (AMFI scheme master data) |
| **Row count** | 40 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| amfi_code | INTEGER | Unique AMFI scheme code (primary key) | Not null, unique |
| fund_house | TEXT | Asset Management Company (AMC) name | Not null |
| scheme_name | TEXT | Full scheme name including plan and option | Not null |
| category | TEXT | Broad SEBI category (e.g. Equity, Debt) | From controlled list |
| sub_category | TEXT | Finer category (e.g. Large Cap, Gilt) | From controlled list |
| plan | TEXT | Plan type | Must be `Regular` or `Direct` |
| launch_date | TEXT | Scheme inception date (ISO `YYYY-MM-DD`) | Valid date ≤ today |
| benchmark | TEXT | Benchmark index the scheme tracks | Not null |
| expense_ratio_pct | REAL | Annual expense ratio (%) | 0 < value ≤ 2.5 |
| exit_load_pct | REAL | Exit load charged on early redemption (%) | ≥ 0 |
| min_sip_amount | INTEGER | Minimum SIP installment (INR) | > 0 |
| min_lumpsum_amount | INTEGER | Minimum lumpsum investment (INR) | > 0 |
| fund_manager | TEXT | Primary fund manager name | Not null |
| risk_category | TEXT | Riskometer grade (e.g. Moderate, High) | From controlled list |
| sebi_category_code | TEXT | SEBI category classification code | Not null |

---

## 2. clean_nav_history

| Field | Detail |
|---|---|
| **Purpose** | Daily Net Asset Value (NAV) per scheme, gap-filled to a complete daily calendar. Powers NAV trend analysis and return calculations. Feeds `fact_nav`. |
| **Source** | `data/processed/clean_nav_history.csv` (cleaned from `02_nav_history.csv`) |
| **Row count** | 64,320 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| amfi_code | INTEGER | Scheme identifier (FK to fund_master) | Not null, must exist in fund_master |
| date | TEXT | Calendar date of the NAV (ISO `YYYY-MM-DD`) | Valid date |
| nav | REAL | Net Asset Value per unit (INR) | > 0 |

---

## 3. clean_investor_transactions

| Field | Detail |
|---|---|
| **Purpose** | Individual investor purchase/redemption transactions with demographics. Powers transaction, inflow/outflow, and demographic analysis. Feeds `fact_transactions`. |
| **Source** | `data/processed/clean_investor_transactions.csv` (cleaned from `08_investor_transactions.csv`) |
| **Row count** | 32,778 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| investor_id | TEXT | Unique investor identifier | Not null |
| transaction_date | TEXT | Date the transaction occurred (ISO `YYYY-MM-DD`) | Valid date |
| amfi_code | INTEGER | Scheme transacted (FK to fund_master) | Not null, must exist in fund_master |
| transaction_type | TEXT | Type of transaction | Must be `SIP`, `Lumpsum`, or `Redemption` |
| amount_inr | REAL | Transaction amount (INR) | > 0 |
| state | TEXT | Investor's state | Not null |
| city | TEXT | Investor's city | Not null |
| city_tier | TEXT | Geographic tier | `T30` (top 30) or `B30` (beyond 30) |
| age_group | TEXT | Investor age band (e.g. 18-25, 56+) | From controlled list |
| gender | TEXT | Investor gender | `Male` / `Female` |
| annual_income_lakh | REAL | Annual income (INR lakh) | ≥ 0 |
| payment_mode | TEXT | Payment channel (e.g. UPI, Cheque, Mandate) | From controlled list |
| kyc_status | TEXT | KYC verification status | Must be `Verified`, `Pending`, or `Rejected` |

---

## 4. clean_scheme_performance

| Field | Detail |
|---|---|
| **Purpose** | Point-in-time performance and risk metrics per scheme. Powers performance dashboards and risk-adjusted comparisons. Feeds `fact_performance`. |
| **Source** | `data/processed/clean_scheme_performance.csv` (cleaned from `07_scheme_performance.csv`) |
| **Row count** | 40 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| amfi_code | INTEGER | Scheme identifier (FK to fund_master) | Not null, must exist in fund_master |
| scheme_name | TEXT | Full scheme name | Not null |
| fund_house | TEXT | Asset Management Company name | Not null |
| category | TEXT | Scheme category | From controlled list |
| plan | TEXT | Plan type | `Regular` / `Direct` |
| return_1yr_pct | REAL | Trailing 1-year return (%) | −100 ≤ value ≤ 200 |
| return_3yr_pct | REAL | Annualized 3-year return (%) | −100 ≤ value ≤ 200 |
| return_5yr_pct | REAL | Annualized 5-year return (%) | −100 ≤ value ≤ 200 |
| benchmark_3yr_pct | REAL | Benchmark's 3-year return (%) | −100 ≤ value ≤ 200 |
| alpha | REAL | Excess return vs benchmark | Numeric |
| beta | REAL | Volatility relative to benchmark | Numeric, typically 0–2 |
| sharpe_ratio | REAL | Return per unit of total risk | Numeric |
| sortino_ratio | REAL | Return per unit of downside risk | Numeric |
| std_dev_ann_pct | REAL | Annualized standard deviation (%) | ≥ 0 |
| max_drawdown_pct | REAL | Largest peak-to-trough decline (%) | ≤ 0 |
| aum_crore | INTEGER | Scheme assets under management (INR crore) | > 0 |
| expense_ratio_pct | REAL | Annual expense ratio (%) | 0.1 ≤ value ≤ 2.5 |
| morningstar_rating | INTEGER | Star rating | Integer 1–5 |
| risk_grade | TEXT | Risk classification | `Low` / `Moderate` / `High` / `Very High` |
| return_1yr_pct_anomaly | BOOLEAN | Flag: 1-yr return outside valid band | True/False |
| return_3yr_pct_anomaly | BOOLEAN | Flag: 3-yr return outside valid band | True/False |
| return_5yr_pct_anomaly | BOOLEAN | Flag: 5-yr return outside valid band | True/False |
| benchmark_3yr_pct_anomaly | BOOLEAN | Flag: benchmark return outside valid band | True/False |
| return_anomaly | BOOLEAN | Flag: any return metric is anomalous | True/False |
| expense_ratio_anomaly | BOOLEAN | Flag: expense ratio outside 0.1–2.5 band | True/False |

> **Note:** The six `*_anomaly` columns are diagnostic flags added during cleaning. They are retained in the CSV for audit but are **not** loaded into `fact_performance`.

---

## 5. aum_by_fund_house

| Field | Detail |
|---|---|
| **Purpose** | Quarter-end Assets Under Management aggregated per fund house. Powers AUM trend and market-share analysis. Feeds `fact_aum`. |
| **Source** | `data/raw/03_aum_by_fund_house.csv` (AMFI industry AUM data) |
| **Row count** | 90 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| date | TEXT | Reporting date, typically quarter-end (ISO `YYYY-MM-DD`) | Valid date |
| fund_house | TEXT | Asset Management Company name | Not null |
| aum_lakh_crore | REAL | Total AUM (INR lakh crore) | ≥ 0 |
| aum_crore | INTEGER | Total AUM (INR crore) | ≥ 0 |
| num_schemes | INTEGER | Number of schemes managed by the AMC | > 0 |

---

## 6. benchmark_indices

| Field | Detail |
|---|---|
| **Purpose** | Daily closing values of market benchmark indices. Used to compare scheme NAV/returns against the market. Feeds `fact_benchmark`. |
| **Source** | `data/raw/10_benchmark_indices.csv` (market index data) |
| **Row count** | 8,050 |

| Column | Data Type | Business Definition | Validation Rules |
|---|---|---|---|
| date | TEXT | Trading date (ISO `YYYY-MM-DD`) | Valid date |
| index_name | TEXT | Benchmark index name (e.g. NIFTY50) | Not null |
| close_value | REAL | Index closing value for the day | > 0 |

---

## Data Quality Summary

The Day 2 cleaning and loading pipeline produced a fully validated, referentially consistent analytics database. Key outcomes:

| Check | Result |
|---|---|
| **NAV history forward-fill** | Expanded from **46,000 → 64,320 rows** by forward-filling missing weekend/holiday dates onto a complete daily calendar (NAVs are only published on trading days). 18,320 dates added. |
| **AMFI validation** | **40 / 40 schemes matched** — every scheme in the fact tables resolves to a record in `fund_master`. No orphaned scheme codes. |
| **Investor transactions** | **No invalid records** — 0 invalid amounts, 0 invalid transaction types, 0 invalid KYC statuses, 0 missing values across 32,778 rows. |
| **Scheme performance** | **No anomalies detected** — all returns within the −100% to 200% band, all expense ratios within 0.1%–2.5%; 0 non-numeric values. |
| **Referential integrity** | `PRAGMA foreign_key_check` returned no violations after loading. |
| **Load completeness** | All source rows loaded with zero loss (AUM 90/90, benchmark 8,050/8,050). |

**Conclusion:** All six datasets passed validation with no data loss or integrity errors. The resulting SQLite star schema is analytics-ready and supports NAV trend analysis, performance metrics, transaction analysis, AUM analysis, and dashboard reporting.
