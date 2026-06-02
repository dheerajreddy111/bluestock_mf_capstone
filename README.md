# 📊 Bluestock Mutual Fund Analytics Platform

> An end-to-end **Mutual Fund Analytics Platform** that ingests AMFI data, performs ETL, stores it in SQLite, computes performance metrics, and visualizes insights through interactive dashboards.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)
[![Status](https://img.shields.io/badge/Status-In%20Progress-yellow.svg)](#)

---

## 📌 Project Overview

The **Bluestock Mutual Fund Analytics Platform** is a capstone project designed to deliver a complete, production-style data analytics workflow for the Indian mutual fund ecosystem.

The platform automates the journey from **raw AMFI data → cleaned datasets → relational storage → performance analytics → visual dashboards**. It pulls live Net Asset Value (NAV) data via public APIs, validates fund metadata against official AMFI codes, and surfaces actionable insights for investors and analysts.

**Core Goal:** Build an end-to-end pipeline that ingests AMFI data, performs ETL, stores data in SQLite, computes performance metrics, and visualizes insights through dashboards.

---

## ✨ Features

- 🔄 **Automated Data Ingestion** — Fetches and consolidates mutual fund datasets from AMFI sources.
- 🧹 **Robust ETL Pipeline** — Cleans, transforms, and validates raw data into analysis-ready form.
- 🗄️ **Relational Storage** — Persists structured data in SQLite via SQLAlchemy ORM.
- ✅ **Data Validation** — Cross-checks AMFI codes and fund master records for integrity.
- 🌐 **Live NAV Integration** — Pulls real-time NAV data from the [mfapi.in](https://www.mfapi.in/) API.
- 📈 **Performance Metrics** — Computes returns, volatility, and risk-adjusted analytics.
- 📊 **Interactive Dashboards** — Visualizes insights using Matplotlib, Seaborn, and Plotly.
- 📝 **Quality Reporting** — Documents data quality observations and validation results.

---

## 🗃️ Dataset Overview

| Attribute | Detail |
|----------|--------|
| **Source** | AMFI (Association of Mutual Funds in India) |
| **Live NAV API** | [mfapi.in](https://www.mfapi.in/) |
| **Datasets Loaded** | 10 datasets |
| **Fund Master** | Validated and analyzed |
| **AMFI Code Validation** | 40/40 codes matched ✅ |
| **Format** | CSV / JSON / API responses |

The datasets include fund master records, scheme metadata, AMFI mapping codes, and historical/live NAV values, forming the foundation for all downstream analytics.

---

## 📁 Folder Structure

```
bluestock_mf_capstone/
├── data/          # Raw and processed datasets
├── scripts/       # ETL, ingestion, and processing scripts
├── notebooks/     # Jupyter notebooks for analysis & exploration
├── sql/           # SQL schemas and queries
├── dashboard/     # Visualization and dashboard code
├── reports/       # Data quality reports & documentation
└── README.md      # Project documentation
```

---

## 🛠️ Technologies Used

| Category | Tools |
|---------|-------|
| **Language** | Python |
| **Data Processing** | Pandas, NumPy |
| **Database** | SQLite, SQLAlchemy |
| **API / Ingestion** | Requests |
| **Notebooks** | Jupyter |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **Version Control** | Git / GitHub |

---

## 🏆 Day 1 Accomplishments

- ✅ **Project structure setup** — Organized modular folder layout.
- ✅ **Dependency installation** — Configured the Python environment.
- ✅ **Data ingestion pipeline** — Built the initial ingestion workflow.
- ✅ **Loaded and validated 10 datasets** — Verified completeness and structure.
- ✅ **Fund master analysis** — Explored and profiled fund master records.
- ✅ **AMFI code validation** — Achieved a perfect **40/40 match**.
- ✅ **Live NAV API integration** — Connected to `mfapi.in` for real-time NAV data.
- ✅ **Data quality observations documented** — Captured findings for future cleanup.

---

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/dheerajreddy111/bluestock_mf_capstone.git
cd bluestock_mf_capstone
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the data ingestion pipeline
```bash
python scripts/ingest_data.py
```

### 5. Launch notebooks for analysis
```bash
jupyter notebook
```

> 💡 Open the notebooks in the `notebooks/` directory to explore the analysis and visualizations.

---

## 🗺️ Project Roadmap (Day 2 – Day 7)

| Day | Milestone | Description |
|-----|-----------|-------------|
| **Day 2** | ETL & Cleaning | Build a robust ETL pipeline to clean and transform raw datasets. |
| **Day 3** | Database Design | Design SQLite schema and load data via SQLAlchemy. |
| **Day 4** | Performance Metrics | Compute returns, CAGR, volatility, and risk-adjusted ratios. |
| **Day 5** | Visualization | Create charts and visual insights with Matplotlib & Seaborn. |
| **Day 6** | Interactive Dashboard | Build interactive Plotly dashboards for fund analytics. |
| **Day 7** | Reporting & Polish | Generate final reports, documentation, and project wrap-up. |

---

## 🚀 Future Enhancements

- 🤖 Integrate **machine learning** models for fund return prediction.
- ☁️ Migrate storage to a **cloud database** (PostgreSQL / BigQuery).
- 🌍 Deploy a **web dashboard** using Streamlit or Dash.
- 🔔 Add **automated alerts** for NAV changes and portfolio movements.
- 📅 Schedule **automated daily data refreshes** via cron jobs.
- 📑 Expand analytics with **benchmark comparisons** and **portfolio optimization**.

---

## 👤 Author

**Dheeraj Reddy Thumma**

> Capstone Project — *Bluestock Mutual Fund Analytics Platform*

---