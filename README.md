# 📊 Bluestock Mutual Fund Analytics Platform

> An end-to-end **Mutual Fund Analytics Platform** that ingests Indian mutual fund data, runs a full ETL pipeline into a star-schema SQLite database, computes institutional-grade performance & risk analytics, serves risk-profiled fund recommendations, and visualizes everything through a 4-page Tableau dashboard.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Scientific-013243.svg)](https://numpy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Star%20Schema-003B57.svg)](https://www.sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-CA4245.svg)](https://www.sqlalchemy.org/)
[![Tableau](https://img.shields.io/badge/Tableau-Dashboard-E97627.svg)](https://www.tableau.com/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626.svg)](https://jupyter.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#-12-license)
[![Status](https://img.shields.io/badge/Status-COMPLETE-brightgreen.svg)](#)

---

## 📑 Table of Contents
1. [Project Overview](#-1-project-overview)
2. [Repository Structure](#-2-repository-structure)
3. [Installation & Setup](#-3-installation--setup)
4. [How to Run the ETL Pipeline](#-4-how-to-run-the-etl-pipeline)
5. [Database Creation](#-5-database-creation)
6. [How to Run Analytics](#-6-how-to-run-analytics)
7. [Dashboard](#-7-dashboard)
8. [Generated Outputs](#-8-generated-outputs)
9. [Technologies Used](#-9-technologies-used)
10. [Key Findings](#-10-key-findings)
11. [Project Deliverables](#-11-project-deliverables)
12. [License](#-12-license)
13. [Author](#-13-author)

---

## 🎯 1. Project Overview

### Problem Statement
Indian mutual fund data is fragmented across NAV histories, scheme metadata, investor transactions, AUM reports, and benchmark indices. Raw datasets are noisy (missing NAVs on weekends/holidays, inconsistent transaction labels, duplicate rows) and are not structured for analysis. Investors and analysts lack a single, query-ready source of truth that combines **performance, risk, and behavioral** insight to support fund-selection decisions.

### Objectives
- Build a **reproducible ETL pipeline** that cleans, validates, and transforms raw fund data.
- Model the data in a **star-schema SQLite warehouse** for fast, query-ready analytics.
- Compute **institutional-grade performance & risk metrics** (CAGR, Sharpe, Sortino, Alpha/Beta, drawdown, VaR/CVaR, tracking error, HHI).
- Deliver a **risk-profile-based recommendation engine**.
- Communicate insight to non-technical stakeholders through an **interactive Tableau dashboard**.

### Business Value
- **Faster, evidence-based fund selection** via a 0–100 composite scorecard and Top-3 recommendations per risk profile.
- **Risk transparency** — tail risk (VaR/CVaR), drawdowns, and sector concentration (HHI) surfaced alongside headline returns.
- **Investor insight** — cohort and SIP-continuity analysis reveal retention and contribution patterns.
- **Reusable data asset** — a clean, documented warehouse any analyst can query immediately.

### Key Outcomes
- ✅ Clean warehouse of **40 schemes**, **64,320** daily NAVs, **32,778** transactions, **8,050** benchmark records.
- ✅ Full performance & advanced-analytics suite across two notebooks.
- ✅ Working recommendation engine (Low / Moderate / High risk).
- ✅ 4-page Tableau dashboard + **34** exported analytics charts.
- ✅ **40/40** AMFI codes validated.

| Metric | Value |
|--------|-------|
| Schemes analyzed | **40** across **10 fund houses** |
| Fund categories | Equity & Debt (**12 sub-categories**) |
| NAV observations | **64,320** daily records (Jan 2022 → May 2026) |
| Investor transactions | **32,778** cleaned records |
| Benchmark index records | **8,050** |
| AMFI code validation | **40 / 40 matched ✅** |

### Architecture

```
        RAW DATA (data/raw)
   fund master · NAV · transactions · AUM · SIP · performance · benchmarks
                    │
        STAGE 1 · ETL (scripts/*.py)        profile → validate → clean → dedup → forward-fill
                    │  → data/processed/*.csv
        STAGE 2 · WAREHOUSE (SQLite)        star schema: 2 dims + 5 facts → data/db/bluestock_mf.db
                    │
   ┌────────────────┼─────────────────────────────┬──────────────────┐
 EDA (nb 03)   Performance (nb 04)        Advanced (nb 05)      Recommender (src/)
   │                │                             │                  │
   └────────────────┴───────────────┬─────────────┴──────────────────┘
                                     ▼
              Reports · Risk metrics · Charts (reports/charts) · Tableau dashboard
```

---

## 📁 2. Repository Structure

```
bluestock_mf_capstone/
├── data/                     # All datasets
│   ├── raw/                  # 10 source CSVs (untouched inputs)
│   ├── processed/            # Cleaned CSVs + analytics outputs & quality reports
│   └── db/                   # bluestock_mf.db — the SQLite warehouse
├── scripts/                  # ETL & database-build pipeline (Python)
├── src/                      # Reusable application code (recommendation engine)
├── notebooks/                # Jupyter analytics notebooks (EDA, performance, advanced)
├── sql/                      # SQL schema (DDL) + analytical queries
├── dashboard/                # Tableau workbooks, per-page data extracts, PNGs, PDF
├── reports/                  # Generated outputs for sharing
│   ├── charts/               # 34 exported PNG visualizations
│   ├── Final_Report.pdf      # Final project report
│   └── Bluestock_MF_Presentation.pptx  # 12-slide capstone deck
├── run_pipeline.py           # Master entry point: runs Validation → ETL → Database
├── requirements.txt          # Pinned Python dependencies
├── LICENSE                   # MIT license
└── README.md
```

**What each major folder contains:**

| Folder | Contents |
|--------|----------|
| **`data/`** | The data lake. `raw/` holds the 10 original source datasets; `processed/` holds 26 cleaned/derived CSVs and data-quality reports; `db/` holds the generated SQLite warehouse. |
| **`scripts/`** | The ETL & warehouse pipeline — profiling, NAV/transaction cleaning, fund-master analysis, and the SQLite loader (`load_to_sqlite.py`). |
| **`src/`** | Reusable, importable application code: `recommender.py`, the risk-profile recommendation engine. |
| **`notebooks/`** | The analysis notebooks: `03_eda_analysis`, `04_performance_analytics`, `05_advanced_analytics`, and `06_bonus_analytics` (Monte Carlo & efficient frontier). |
| **`sql/`** | `schema.sql` (star-schema DDL) and `queries.sql` (analytical queries). |
| **`dashboard/`** | Tableau workbooks (`.twb`), per-page data extracts in `Dashboard_Data/`, page PNGs, and `dashboard.pdf`. |
| **`reports/`** | Sharable outputs: `charts/` (34 publication-quality PNGs), `Final_Report.pdf` (final project report), and `Bluestock_MF_Presentation.pptx` (12-slide capstone deck). |
| **Documentation** | Kept alongside the code rather than in a separate `docs/` folder: `dashboard/dashboard_documentation.md` (dashboard guide), `sql/schema.sql` (schema), and this `README.md`. |

---

## ⚙️ 3. Installation & Setup

### Step 1 — Clone the repository
```bash
git clone https://github.com/dheerajreddy111/bluestock_mf_capstone.git
cd bluestock_mf_capstone
```

### Step 2 — Create & activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Verify dependencies
```bash
python -c "import pandas, numpy, scipy, sqlalchemy, matplotlib, seaborn, plotly, openpyxl, kaleido; print('All dependencies OK')"
pip check
```

> Requires **Python 3.11+**. Run all commands below from the **project root**.

---

## 🔄 4. How to Run the ETL Pipeline

### ⭐ One command (recommended)

`run_pipeline.py` is the master entry point. It runs the entire data-engineering build — **Validation → ETL → Database** — in the correct order, using `subprocess` to call the existing scripts. It is **fail-fast** (stops on the first error), validates that each step's expected output files exist, and prints a stage-by-stage progress log plus a final summary.

```bash
python run_pipeline.py
```

The full build completes in **~3 seconds** and ends with `✅ SUCCESS — database at data/db/bluestock_mf.db`.

| Stage | Scripts executed |
|-------|------------------|
| **1 · Validation** | `data_ingestion.py` → `inspect_nav_history.py` → `check_nav_date_gaps.py` |
| **2 · ETL** | `clean_nav_history.py` → `clean_investor_transactions.py` → `fund_master_analysis.py` |
| **3 · Database Build** | `load_to_sqlite.py` |

> Scope is data-engineering only — the runner does **not** execute notebooks, analytics, or dashboards. Run those separately (see §6). It also runs every script with the project root as the working directory, so it works no matter where you launch it from.

### Manual run (individual scripts)

You can also run each step yourself, in order, from the project root:

| # | Command | Expected output |
|---|---------|-----------------|
| 1 | `python scripts/data_ingestion.py` | `data/processed/ingestion_summary.csv` (per-file profile) |
| 2 | `python scripts/inspect_nav_history.py` | `data/processed/nav_profile_summary.csv` |
| 3 | `python scripts/check_nav_date_gaps.py` | `data/processed/nav_date_gap_report.csv` |
| 4 | `python scripts/clean_nav_history.py` | `data/processed/clean_nav_history.csv` + `nav_quality_report.csv` |
| 5 | `python scripts/clean_investor_transactions.py` | `data/processed/clean_investor_transactions.csv` + quality report |
| 6 | `python scripts/fund_master_analysis.py` | `data/processed/fund_master_summary.xlsx` |
| 7 | `python scripts/load_to_sqlite.py` | `data/db/bluestock_mf.db` + `load_summary.csv` |

Each script prints a timestamped log and a summary table to the console.

---

## 🗄️ 5. Database Creation

### How it is generated
```bash
python scripts/load_to_sqlite.py
```
The loader performs a clean, repeatable build: it drops any existing database, executes `sql/schema.sql` to create the tables, derives `dim_date` from every dated dataset, loads `dim_fund` and all fact tables, verifies row counts, and writes `data/processed/load_summary.csv`.

### Location
```
data/db/bluestock_mf.db
```

### Schema (star schema — `sql/schema.sql`)

| Type | Table | Rows | Description |
|------|-------|-----:|-------------|
| Dimension | `dim_fund` | 40 | Scheme master: house, category, manager, expense ratio, risk |
| Dimension | `dim_date` | 1,608 | Calendar attributes (year/quarter/month/weekend/month-end) |
| Fact | `fact_nav` | 64,320 | Daily NAV per scheme |
| Fact | `fact_transactions` | 32,778 | Investor transactions (SIP / Lumpsum / Redemption) |
| Fact | `fact_performance` | 40 | Point-in-time return & risk measures |
| Fact | `fact_aum` | 90 | AUM by fund house over time |
| Fact | `fact_benchmark` | 8,050 | Benchmark index closing values |

Ready-to-use analytical queries live in `sql/queries.sql`.

---

## 📓 6. How to Run Analytics

Launch Jupyter from the project root and run the notebooks **in order**:
```bash
jupyter notebook
```

| Notebook | Focus | Selected sections |
|----------|-------|-------------------|
| **`notebooks/03_eda_analysis.ipynb`** | Exploratory Data Analysis | Fund category analysis, AUM analysis, investor behavior, transaction analysis, benchmark exploration |
| **`notebooks/04_performance_analytics.ipynb`** | Performance Analytics | CAGR, Sharpe, Sortino, Alpha/Beta, Maximum Drawdown, Fund Scorecard (0–100), Benchmark Comparison, Tracking Error |
| **`notebooks/05_advanced_analytics.ipynb`** | Advanced Analytics | Historical VaR & CVaR, Rolling Sharpe, Investor Cohort Analysis, SIP Continuity, Recommendation Engine, Sector Concentration (HHI), Executive Summary |
| **`notebooks/06_bonus_analytics.ipynb`** | Bonus Analytics | Monte Carlo NAV projection (5-yr, uncertainty bands), Markowitz Efficient Frontier (top-5 funds) |

**Recommendation engine** (used by notebook 05, also runnable standalone):
```bash
python src/recommender.py            # prints Top-3 funds per risk profile
```
```python
from src.recommender import recommend
recommend("moderate")                # alias-tolerant: low / moderate / high
```

**Bonus analytics notebook** — `notebooks/06_bonus_analytics.ipynb`:
- **Monte Carlo** — projects the top-ranked fund's NAV 5 years out (1,000 simulated paths, percentile uncertainty bands) → `reports/charts/monte_carlo_nav_projection.png`, `data/processed/monte_carlo_projection.csv`
- **Efficient Frontier** — optimises a long-only portfolio of the top-5 scorecard funds (max-Sharpe & min-volatility) → `reports/charts/efficient_frontier.png`, `data/processed/efficient_frontier_portfolios.csv`

---

## 📊 7. Dashboard

An interactive **4-page Tableau dashboard** turns the analytics into a stakeholder-ready story.

| Page | Title | Purpose |
|------|-------|---------|
| **1** | **Industry Overview** | KPI cards, AUM trends, fund-house analysis |
| **2** | **Fund Performance** | Fund scorecards, performance comparison |
| **3** | **Investor Analytics** | Transaction insights, demographic analysis |
| **4** | **SIP & Market Trends** | SIP growth, category trends |

### How to open the Tableau workbook
1. Install **Tableau Desktop** or the free **Tableau Public**.
2. Open the workbooks in `dashboard/` (one `.twb` per page, e.g. `Industry Overview.twb`, `Fund_Performance.twb`, `Investor Analytics.twb`, `SIP & Market Trends.twb`).
3. Each workbook reads its extracts from `dashboard/Dashboard_Data/`.

### Prefer a quick look?
- Page previews: `dashboard/page1_industry_overview.png` … `page4_sip_market_trends.png`
- Full export: `dashboard/dashboard.pdf`
- Dashboard guide: `dashboard/dashboard_documentation.md`

> **Tableau Public:** the workbooks are publish-ready; once a public version is hosted, the link will be added here.

---

## 📦 8. Generated Outputs

| Output type | Location | Examples |
|-------------|----------|----------|
| **SQLite database** | `data/db/` | `bluestock_mf.db` |
| **Cleaned CSV datasets** | `data/processed/` | `clean_nav_history.csv`, `clean_investor_transactions.csv` |
| **Analytics & risk reports** | `data/processed/` | `cagr_comparison.csv`, `sharpe_rankings.csv`, `sortino_rankings.csv`, `alpha_beta.csv`, `max_drawdown.csv`, `tracking_error.csv`, `var_cvar_report.csv`, `rolling_sharpe_summary.csv`, `sector_hhi.csv`, `fund_scorecard.csv` |
| **Data-quality reports** | `data/processed/` | `nav_quality_report.csv`, `investor_transaction_quality_report.csv`, `amfi_validation_report.csv`, `load_summary.csv` |
| **Recommendation outputs** | `data/processed/` | `fund_recommendations.csv` (served by `src/recommender.py`) |
| **Charts / visualizations** | `reports/charts/` | 34 PNGs (e.g. `top_10_cagr.png`, `top_sharpe_ratio.png`, `var_cvar_risk_rankings.png`, `monte_carlo_nav_projection.png`, `efficient_frontier.png`) |
| **Excel summary** | `data/processed/` | `fund_master_summary.xlsx` |
| **Dashboard exports** | `dashboard/` | page PNGs + `dashboard.pdf` |

---

## 🛠️ 9. Technologies Used

| Category | Tools |
|---------|-------|
| **Language** | **Python 3.11** |
| **Data Processing** | **Pandas**, **NumPy**, python-dateutil |
| **Scientific / Stats** | **SciPy** (`linregress` for Alpha/Beta) |
| **Database** | **SQLite**, SQLAlchemy |
| **Notebooks** | **Jupyter Notebook** |
| **Visualization (Python)** | **Matplotlib**, **Seaborn**, **Plotly** (+ Kaleido), openpyxl |
| **Business Intelligence** | **Tableau** (4-page interactive dashboard) |
| **Version Control** | Git / GitHub |

---

## 🔑 10. Key Findings

> Computed directly from the project dataset (40 schemes, Jan 2022 – May 2026).

### Risk & performance analytics
- **Best risk-adjusted performers (Sharpe):** Mirae Asset Large Cap Fund (**1.07**), Kotak Flexicap Fund (**0.97**), Mirae Asset Tax Saver Fund (**0.92**).
- **Top 3-year CAGR:** Axis Midcap Fund (**~35%**), Mirae Asset Large Cap Fund (**~34%**), ICICI Prudential Bluechip Fund (**~33%**) — mid- and large-cap equity led growth.
- **Sector concentration (HHI):** the most concentrated equity portfolios (e.g. Axis Bluechip, ~3.4 effective sectors) carry diversification risk invisible in headline returns.

### Investor behavior
- **32,778** cleaned transactions powered cohort and SIP-continuity analysis, exposing SIP persistence and drop-off patterns across demographics and city tiers.

### Fund recommendations
- The engine reliably maps risk profiles to suitable funds: **moderate** → large-/flexi-cap equity; **low** → Gilt / Short-Duration debt (e.g. SBI Magnum Gilt, HDFC Short Term Debt); **high** → mid-/small-cap.

### Dashboard insights
- Industry AUM and SIP inflows trend upward across the window; equity dominates fund-house AUM, while the performance page makes the scorecard ranking instantly comparable for non-technical users.

### Data quality
- **40/40** AMFI codes validated; weekend/holiday NAV gaps systematically forward-filled into a complete **64,320-row** daily history.

---

## 📋 11. Project Deliverables

- 🗄️ **Database** — `data/db/bluestock_mf.db`, a star-schema SQLite warehouse (2 dimensions + 5 facts).
- 📓 **Notebooks** — EDA, Performance Analytics, and Advanced Analytics (`notebooks/`).
- 📊 **Dashboard** — 4-page interactive Tableau workbook set (`dashboard/`).
- 📑 **Reports** — analytics, risk-metric, and data-quality CSVs (`data/processed/`).
- 🖼️ **Visualizations** — 34 publication-quality charts (`reports/charts/`).
- 🎯 **Recommendation engine** — `src/recommender.py` + `fund_recommendations.csv`.
- 🧪 **Bonus analytics** — `notebooks/06_bonus_analytics.ipynb`: Monte Carlo NAV projection & Markowitz efficient frontier.
- 📄 **Final report & deck** — `reports/Final_Report.pdf` and `reports/Bluestock_MF_Presentation.pptx`.
- 📚 **Documentation** — `dashboard/dashboard_documentation.md`, schema & queries (`sql/`), and this `README.md`.

---

## 📄 12. License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for full text.

---

## 👤 13. Author

**Dheeraj Reddy Thumma**
Data Analyst — *Bluestock Mutual Fund Analytics Platform* (Internship Capstone)

> 📌 **Project Status: COMPLETE** — all ETL, warehouse, analytics, recommendation, and dashboard components delivered.
