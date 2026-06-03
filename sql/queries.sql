-- =============================================================================
-- queries.sql
-- Bluestock Mutual Fund Analytics Capstone - Day 2
-- 10 analytical SQLite queries against the star schema.
--
-- Tables: dim_fund, dim_date,
--         fact_nav, fact_transactions, fact_performance, fact_aum, fact_benchmark
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. Top 5 funds by AUM
-- Uses the per-scheme AUM captured in fact_performance, joined to dim_fund
-- for readable scheme details. Returns the five largest schemes by AUM.
-- -----------------------------------------------------------------------------
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM fact_performance AS p
JOIN dim_fund AS f
    ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- -----------------------------------------------------------------------------
-- 2. Average NAV per month
-- Averages the daily NAV across all schemes for each calendar month, using
-- dim_date for the year/month labels. Useful for an overall NAV trend line.
-- -----------------------------------------------------------------------------
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    COUNT(*)             AS nav_observations
FROM fact_nav AS n
JOIN dim_date AS d
    ON d.date_key = n.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- -----------------------------------------------------------------------------
-- 3. SIP year-over-year (YoY) growth
-- Totals SIP inflows per year, then uses the LAG window function to compare
-- each year against the previous one and express growth as a percentage.
-- -----------------------------------------------------------------------------
WITH sip_yearly AS (
    SELECT
        d.year                AS year,
        SUM(t.amount_inr)     AS sip_amount
    FROM fact_transactions AS t
    JOIN dim_date AS d
        ON d.date_key = t.date_key
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
)
SELECT
    year,
    sip_amount,
    LAG(sip_amount) OVER (ORDER BY year) AS prev_year_amount,
    ROUND(
        100.0 * (sip_amount - LAG(sip_amount) OVER (ORDER BY year))
        / LAG(sip_amount) OVER (ORDER BY year),
        2
    ) AS yoy_growth_pct
FROM sip_yearly
ORDER BY year;


-- -----------------------------------------------------------------------------
-- 4. Transactions by state
-- Counts transactions and totals the amount invested per state, so we can see
-- which regions are most active. Ordered by total amount.
-- -----------------------------------------------------------------------------
SELECT
    state,
    COUNT(*)                  AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
WHERE state IS NOT NULL
GROUP BY state
ORDER BY total_amount_inr DESC;


-- -----------------------------------------------------------------------------
-- 5. Funds with expense ratio below 1%
-- Lists low-cost schemes (expense ratio under 1%) from the fund dimension.
-- Lower expense ratios generally mean cheaper funds for investors.
-- -----------------------------------------------------------------------------
SELECT
    amfi_code,
    scheme_name,
    fund_house,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;


-- -----------------------------------------------------------------------------
-- 6. Top 10 funds by 5-year return
-- Ranks schemes on their 5-year percentage return (long-term performance),
-- ignoring rows where the 5-year return is missing.
-- -----------------------------------------------------------------------------
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.return_5yr_pct
FROM fact_performance AS p
JOIN dim_fund AS f
    ON f.amfi_code = p.amfi_code
WHERE p.return_5yr_pct IS NOT NULL
ORDER BY p.return_5yr_pct DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 7. Fund house market share by AUM
-- Uses the most recent AUM snapshot per fund house, then computes each house's
-- share of the total market AUM as a percentage. Shows industry concentration.
-- -----------------------------------------------------------------------------
WITH latest_date AS (
    -- Find the newest AUM reporting date in the data.
    SELECT MAX(date_key) AS max_date_key
    FROM fact_aum
),
latest_aum AS (
    -- Keep only the AUM rows from that newest date.
    SELECT
        a.fund_house,
        a.aum_crore
    FROM fact_aum AS a
    JOIN latest_date AS ld
        ON a.date_key = ld.max_date_key
)
SELECT
    fund_house,
    aum_crore,
    ROUND(
        100.0 * aum_crore / SUM(aum_crore) OVER (),
        2
    ) AS market_share_pct
FROM latest_aum
ORDER BY aum_crore DESC;


-- -----------------------------------------------------------------------------
-- 8. Category-wise average returns
-- Averages 1/3/5-year returns within each fund category (e.g. Large Cap, Gilt)
-- so categories can be compared at a glance.
-- -----------------------------------------------------------------------------
SELECT
    f.category,
    COUNT(*)                          AS fund_count,
    ROUND(AVG(p.return_1yr_pct), 2)   AS avg_return_1yr_pct,
    ROUND(AVG(p.return_3yr_pct), 2)   AS avg_return_3yr_pct,
    ROUND(AVG(p.return_5yr_pct), 2)   AS avg_return_5yr_pct
FROM fact_performance AS p
JOIN dim_fund AS f
    ON f.amfi_code = p.amfi_code
GROUP BY f.category
ORDER BY avg_return_3yr_pct DESC;


-- -----------------------------------------------------------------------------
-- 9. Highest Sharpe ratio funds
-- Ranks schemes by Sharpe ratio (risk-adjusted return). A higher Sharpe ratio
-- means better return per unit of risk. Top 10 shown.
-- -----------------------------------------------------------------------------
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.sharpe_ratio,
    p.return_3yr_pct
FROM fact_performance AS p
JOIN dim_fund AS f
    ON f.amfi_code = p.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 10. Largest drawdown funds
-- Finds the schemes that fell the most from a peak (max_drawdown_pct is the
-- most negative). These are the riskiest funds on the downside. Top 10 shown.
-- -----------------------------------------------------------------------------
SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.max_drawdown_pct,
    p.risk_grade
FROM fact_performance AS p
JOIN dim_fund AS f
    ON f.amfi_code = p.amfi_code
WHERE p.max_drawdown_pct IS NOT NULL
ORDER BY p.max_drawdown_pct ASC
LIMIT 10;
