# API Validation Note

During Day 1 live NAV ingestion, all API requests completed successfully.

However, validation of scheme metadata returned by mfapi.in indicated that some
provided scheme codes resolved to different scheme names than those listed in the
project specification.

The ETL pipeline preserves the actual scheme metadata returned by the API
(scheme_name, fund_house, category), ensuring traceability and preventing
mislabelled downstream analysis.

This issue appears to originate from external API/reference-code discrepancies
rather than the ingestion implementation.