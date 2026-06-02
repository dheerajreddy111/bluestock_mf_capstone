# Day 1 Findings

## Dataset Validation

* Successfully loaded all 10 provided datasets.
* Generated ingestion summary for all files.
* No major ingestion failures observed.

## Fund Master Summary

* Total Schemes: 40
* Fund Houses: 10
* Categories: 2
* Sub-Categories: 12
* Risk Categories: 5

### Category Distribution

* Equity: 34 schemes
* Debt: 6 schemes

### Largest Fund Houses

* SBI Mutual Fund: 5 schemes
* HDFC Mutual Fund: 5 schemes
* ICICI Prudential MF: 5 schemes
* Nippon India MF: 5 schemes

### Risk Distribution

* Moderate: 16 schemes
* High: 8 schemes
* Very High: 6 schemes
* Low: 6 schemes
* Moderately High: 4 schemes

## AMFI Code Validation

* Codes in Fund Master: 40
* Codes in NAV History: 40
* Matching Codes: 40
* Match Rate: 100%
* Missing Codes: 0

## Data Quality Findings

### SIP Dataset

* 12 missing values detected in `04_monthly_sip_inflows.csv`.
* Marked for investigation during Day 2 cleaning.

### Live NAV API

* Successfully fetched approximately 19,798 NAV records.
* Some provided scheme labels did not match metadata returned by MFAPI.
* Actual API metadata was preserved and documented for traceability.

## Day 1 Status

✅ Data ingestion completed
✅ Dataset validation completed
✅ API integration completed
