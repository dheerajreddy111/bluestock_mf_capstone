# Bluestock Mutual Fund Analytics — Dashboard Documentation

**Project:** Bluestock Mutual Fund Analytics Capstone  
**Day:** 5 — Dashboard Development  
**Tool:** Tableau Public  
**Author:** Bluestock Fintech Intern  
**Date:** June 2026  

---

## Project Overview

This dashboard presents a comprehensive analysis of the Indian mutual fund industry using real AMFI data. It covers industry-level KPIs, fund performance metrics, investor behaviour analytics, and SIP market trends across 4 interactive dashboard pages.

---

## Folder Structure

```
dashboard/
├── bluestock_mf_dashboards       # Main Tableau workbook
├── page1_industry_overview.pdf        # Page 1 export
├── page2_fund_performance.pdf         # Page 2 export
├── page3_investor_analytics.pdf       # Page 3 export
├── page4_sip_market_trends.pdf        # Page 4 export
├── page1_industry_overview.png        # Page 1 screenshot
├── page2_fund_performance.png         # Page 2 screenshot
├── page3_investor_analytics.png       # Page 3 screenshot
└── page4_sip_market_trends.png        # Page 4 screenshot
```

---

## Data Sources

### Page 1 — Industry Overview
| File | Source Folder | Description |
|------|--------------|-------------|
| `03_aum_by_fund_house.csv` | raw/ | AUM by fund house (monthly) |
| `04_monthly_sip_inflows.csv` | raw/ | Monthly SIP inflow data |
| `06_industry_folio_count.csv` | raw/ | Industry folio count (monthly) |
| `01_fund_master.csv` | raw/ | Master list of all schemes |
| `clean_nav_history.csv` | processed/ | Cleaned NAV history for trend |

### Page 2 — Fund Performance
| File | Source Folder | Description |
|------|--------------|-------------|
| `fund_scorecard.csv` | processed/ | Fund scoring and rankings |
| `alpha_beta.csv` | processed/ | Alpha and beta metrics |
| `sharpe_rankings.csv` | processed/ | Sharpe ratio rankings |
| `sortino_rankings.csv` | processed/ | Sortino ratio rankings |
| `tracking_error.csv` | processed/ | Tracking error data |
| `max_drawdown.csv` | processed/ | Maximum drawdown data |
| `cagr_comparison.csv` | processed/ | 1yr and 3yr CAGR comparison |

### Page 3 — Investor Analytics
| File | Source Folder | Description |
|------|--------------|-------------|
| `clean_investor_transactions.csv` | processed/ | Cleaned investor transaction data |

### Page 4 — SIP & Market Trends
| File | Source Folder | Description |
|------|--------------|-------------|
| `04_monthly_sip_inflows.csv` | raw/ | Monthly SIP inflow data |
| `05_category_inflows.csv` | raw/ | Category-wise net inflows |

---

## Dashboard Pages

---

### Page 1 — Industry Overview

**Title:** Bluestock Mutual Fund Analytics — Industry Overview  
**Purpose:** High-level snapshot of the Indian mutual fund industry.

#### KPI Cards
| KPI | Value | Data Source | Field Used |
|-----|-------|-------------|------------|
| Total AUM | ₹62.74 Lakh Crore | 03_aum_by_fund_house.csv | Aum Lakh Crore (latest month) |
| SIP Inflow | ₹31,002 Crore | 04_monthly_sip_inflows.csv | Sip Inflow Crore (latest month) |
| Total Folios | 26.12 Crore | 06_industry_folio_count.csv | Total Folios Crore (latest month) |
| Number of Schemes | 40 | 01_fund_master.csv | Count Distinct (Scheme Name) |

#### Charts
| Chart | Type | X Axis | Y Axis | Data Source |
|-------|------|--------|--------|-------------|
| Industry AUM Trend | Line chart | Month (Date) | SUM(Nav) | clean_nav_history.csv |
| Top Fund Houses by AUM | Horizontal bar | Aum Lakh Crore | Fund House | 03_aum_by_fund_house.csv |

#### Key Insights
- SBI Mutual Fund leads with ₹84.91 Lakh Crore AUM
- Industry AUM shows consistent upward trend from 2022 to 2025
- ICICI Prudential and HDFC follow as second and third largest fund houses

---

### Page 2 — Fund Performance

**Title:** Bluestock Mutual Fund Analytics — Fund Performance  
**Purpose:** Analyse individual fund performance using risk-return metrics.

#### Charts
| Chart | Type | Description | Data Source |
|-------|------|-------------|-------------|
| Return vs Risk | Scatter plot | Return Rank (X) vs Sharpe Rank (Y), sized by Fund Score, colored by Category | fund_scorecard.csv |
| Fund Scorecard | Text table | Scheme Name, Category, Fund Score, Overall Rank, Return Rank, Sharpe Rank | fund_scorecard.csv |
| Fund CAGR Comparison | Horizontal bar | 1-year CAGR by scheme, colored by Category | cagr_comparison.csv |

#### Key Insights
- Equity funds (orange) dominate the high-return quadrant
- Debt funds (blue) cluster in the lower-risk, lower-return zone
- HDFC Mid-Cap and Axis Midcap show strong risk-adjusted performance

---

### Page 3 — Investor Analytics

**Title:** Bluestock Mutual Fund Analytics — Investor Analytics  
**Purpose:** Understand investor behaviour, demographics, and transaction patterns.

#### Charts
| Chart | Type | Description | Data Source |
|-------|------|-------------|-------------|
| State Transaction Amount | Horizontal bar | Total transaction amount by state, sorted descending | clean_investor_transactions.csv |
| Transaction Type Split | Pie chart | SIP vs Lumpsum vs Redemption by Amount INR | clean_investor_transactions.csv |
| Age Group vs SIP Amount | Vertical bar | Average Amount INR by Age Group | clean_investor_transactions.csv |
| Monthly Transaction Trend | Multi-line chart | Monthly Amount INR by Transaction Type | clean_investor_transactions.csv |

#### Fields Used
| Field | Type | Used In |
|-------|------|---------|
| State | Dimension | State Transaction Amount |
| Transaction Type | Dimension | Pie chart, Monthly Trend |
| Amount INR | Measure | All charts |
| Age Group | Dimension | Age Group chart |
| Transaction Date | Date | Monthly Trend |

#### Key Insights
- Punjab leads in total transaction amount
- Lumpsum transactions account for the largest share by value
- All age groups show similar average SIP amounts (~₹1 Lakh)
- Transaction volumes remain stable from Jan 2024 to Apr 2025

---

### Page 4 — SIP & Market Trends

**Title:** Bluestock Mutual Fund Analytics — SIP & Market Trends  
**Purpose:** Track SIP growth and category-wise inflow trends over time.

#### Charts
| Chart | Type | Description | Data Source |
|-------|------|-------------|-------------|
| SIP Inflow Trend | Line chart | Monthly SIP Inflow Crore from 2022–2025 | 04_monthly_sip_inflows.csv |
| Category Inflow Heatmap | Heatmap (Square marks) | Net Inflow Crore by Category and Month | 05_category_inflows.csv |
| Top Categories by Inflow | Horizontal bar | Total Net Inflow Crore by Category, sorted descending | 05_category_inflows.csv |

#### Key Insights
- SIP inflows grew from ~₹12,000 Crore (Jan 2022) to ~₹31,000 Crore (Dec 2025)
- Liquid funds dominate net inflows at ₹4,51,275 Crore total
- Sectoral/Thematic funds are the second largest category by inflows
- Heatmap shows consistent inflows across categories with Liquid always darkest

---

## Tableau Sheets Summary

| Sheet Name | Chart Type | Data Source | Dashboard |
|------------|-----------|-------------|-----------|
| Top Fund Houses by AUM | Horizontal bar | 03_aum_by_fund_house | Page 1 |
| Industry AUM Trend | Line chart | clean_nav_history | Page 1 |
| KPI Total AUM | Text/number | 03_aum_by_fund_house | Page 1 |
| KPI SIP Inflow | Text/number | 04_monthly_sip_inflows | Page 1 |
| KPI Folios | Text/number | 06_industry_folio_count | Page 1 |
| KPI Schemes | Text/number | 01_fund_master | Page 1 |
| Fund Scorecard | Text table | fund_scorecard | Page 2 |
| Return vs Risk | Scatter plot | fund_scorecard | Page 2 |
| Fund CAGR Comparison | Horizontal bar | cagr_comparison | Page 2 |
| Transaction Type Split | Pie chart | clean_investor_transactions | Page 3 |
| State Transaction Amount | Horizontal bar | clean_investor_transactions | Page 3 |
| Age Group vs SIP Amount | Vertical bar | clean_investor_transactions | Page 3 |
| Monthly Transaction Trend | Multi-line | clean_investor_transactions | Page 3 |
| Category Inflow Heatmap | Heatmap | 05_category_inflows | Page 4 |
| SIP Inflow Trend | Line chart | 04_monthly_sip_inflows | Page 4 |
| Top Categories by Inflow | Horizontal bar | 05_category_inflows | Page 4 |

---

## Technical Notes

- **Tool:** Tableau Public (Mac)
- **Dashboard Size:** Generic Desktop 1366 x 768 px
- **Data format:** CSV (Text file connection in Tableau)
- **Date filters:** Applied to limit data to 2022–2025 range
- **Aggregations used:** SUM, AVG, COUNT DISTINCT
- **Color encoding:** Category (Debt = Blue, Equity = Orange), Amount intensity (heatmap)

---

## Limitations

- `01_fund_master.csv` contains 40 schemes (sample dataset, not full 1908 universe)
- `Cagr 5Yr` column in `cagr_comparison.csv` is mostly null
- NAV data used as proxy for AUM trend (clean_nav_history.csv)
- Investor transaction data covers Jan 2024 – Apr 2025 only

---

## Day 5 Completion Status

| Task | Status |
|------|--------|
| Connect all CSV data sources | ✅ Complete |
| Build Page 1 — Industry Overview | ✅ Complete |
| Build Page 2 — Fund Performance | ✅ Complete |
| Build Page 3 — Investor Analytics | ✅ Complete |
| Build Page 4 — SIP & Market Trends | ✅ Complete |
| Export 4 screenshots (PNG) | ✅ Complete |
| Export 4 PDFs | ✅ Complete |
| Dashboard documentation | ✅ Complete |

---

*Bluestock Fintech — Mutual Fund Analytics Capstone | Day 5 of 5*
