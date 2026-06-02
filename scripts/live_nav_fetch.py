"""Fetch live historical NAV data from the MFAPI service.

For the Bluestock Mutual Fund Analytics Capstone, this script pulls historical
NAV history for a fixed set of large-cap schemes from https://api.mfapi.in,
persists one CSV per scheme, and writes a consolidated fetch summary report.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
API_BASE_URL = "https://api.mfapi.in/mf/{scheme_code}"
REQUEST_TIMEOUT = 30  # seconds
RAW_OUTPUT_DIR = Path("data/raw/live_nav")
SUMMARY_PATH = Path("data/processed/nav_fetch_summary.csv")

# scheme_code -> output filename
SCHEMES: dict[str, str] = {
    "125497": "hdfc_top_100_nav.csv",
    "119551": "sbi_bluechip_nav.csv",
    "120503": "icici_bluechip_nav.csv",
    "118632": "nippon_large_cap_nav.csv",
    "119092": "axis_bluechip_nav.csv",
    "120841": "kotak_bluechip_nav.csv",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("live_nav_fetch")


def fetch_scheme(scheme_code: str, session: requests.Session) -> dict:
    """Fetch the raw JSON payload for a single scheme code."""
    url = API_BASE_URL.format(scheme_code=scheme_code)
    logger.info("Fetching scheme %s: %s", scheme_code, url)

    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    payload = response.json()
    if payload.get("status") != "SUCCESS":
        raise ValueError(f"API returned non-success status for {scheme_code}")
    if not payload.get("data"):
        raise ValueError(f"No NAV data returned for scheme {scheme_code}")
    return payload


def build_nav_dataframe(payload: dict, scheme_code: str) -> pd.DataFrame:
    """Convert the NAV history payload into a typed, sorted dataframe."""
    meta = payload.get("meta", {})
    df = pd.DataFrame(payload["data"])

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"]).sort_values("date").reset_index(drop=True)

    # Enrich each row with scheme metadata for traceability.
    df.insert(0, "scheme_code", meta.get("scheme_code", scheme_code))
    df["scheme_name"] = meta.get("scheme_name")
    df["fund_house"] = meta.get("fund_house")
    df["scheme_category"] = meta.get("scheme_category")
    return df


def main() -> int:
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    summary_records: list[dict] = []

    with requests.Session() as session:
        for scheme_code, filename in SCHEMES.items():
            record = {
                "scheme_code": scheme_code,
                "filename": filename,
                "scheme_name": None,
                "fund_house": None,
                "records": 0,
                "start_date": None,
                "end_date": None,
                "status": "FAILED",
                "error": None,
            }
            try:
                payload = fetch_scheme(scheme_code, session)
                df = build_nav_dataframe(payload, scheme_code)

                output_path = RAW_OUTPUT_DIR / filename
                df.to_csv(output_path, index=False)

                meta = payload.get("meta", {})
                record.update(
                    {
                        "scheme_name": meta.get("scheme_name"),
                        "fund_house": meta.get("fund_house"),
                        "records": len(df),
                        "start_date": df["date"].min().date().isoformat(),
                        "end_date": df["date"].max().date().isoformat(),
                        "status": "SUCCESS",
                    }
                )
                logger.info(
                    "Saved %s rows to %s (%s)",
                    f"{len(df):,}",
                    output_path,
                    meta.get("scheme_name"),
                )

            except requests.exceptions.Timeout as exc:
                record["error"] = f"Timeout after {REQUEST_TIMEOUT}s"
                logger.error("Timeout fetching scheme %s: %s", scheme_code, exc)
            except requests.exceptions.RequestException as exc:
                record["error"] = str(exc)
                logger.error("Request failed for scheme %s: %s", scheme_code, exc)
            except (ValueError, KeyError) as exc:
                record["error"] = str(exc)
                logger.error("Data error for scheme %s: %s", scheme_code, exc)
            except Exception as exc:  # noqa: BLE001 - per-scheme safety net
                record["error"] = str(exc)
                logger.exception("Unexpected error for scheme %s", scheme_code)

            summary_records.append(record)

    summary_df = pd.DataFrame(summary_records)
    summary_df.to_csv(SUMMARY_PATH, index=False)
    logger.info("Fetch summary saved to: %s", SUMMARY_PATH)

    succeeded = int((summary_df["status"] == "SUCCESS").sum())
    failed = len(summary_df) - succeeded

    print("\n" + "=" * 60)
    print("LIVE NAV FETCH SUMMARY")
    print("=" * 60)
    print(f"Schemes requested : {len(summary_df)}")
    print(f"Succeeded         : {succeeded}")
    print(f"Failed            : {failed}")
    print(f"Total NAV rows    : {int(summary_df['records'].sum()):,}")
    print(f"Output directory  : {RAW_OUTPUT_DIR}")
    print(f"Summary report    : {SUMMARY_PATH}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
