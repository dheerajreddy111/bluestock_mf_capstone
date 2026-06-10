"""run_pipeline.py — Bluestock Mutual Fund Analytics data-engineering pipeline.

Master entry point that runs the reproducible build, in order:

    Stage 1  Validation       data_ingestion, inspect_nav_history, check_nav_date_gaps
    Stage 2  ETL              clean_nav_history, clean_investor_transactions, fund_master_analysis
    Stage 3  Database build   load_to_sqlite

Scope: data-engineering only. Notebooks, analytics, dashboards, and report
generation are intentionally excluded.

Design:
    * Orchestration only — each step is an EXISTING script run via subprocess.
      No ETL logic is duplicated and no script is modified.
    * Scripts run with cwd = project root so working-directory-relative paths
      resolve correctly regardless of where this file is launched from.
    * Fail-fast: the first failing step (non-zero exit or missing expected
      output) stops the pipeline with a clear message and exit code 1.

Usage:
    python run_pipeline.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Each stage: (title, [(script, [expected output files]), ...]).
# Paths are relative to the project root.
PIPELINE: list[tuple[str, list[tuple[str, list[str]]]]] = [
    ("Stage 1 — Validation", [
        ("scripts/data_ingestion.py",
         ["data/processed/ingestion_summary.csv"]),
        ("scripts/inspect_nav_history.py",
         ["data/processed/nav_profile_summary.csv"]),
        ("scripts/check_nav_date_gaps.py",
         ["data/processed/nav_date_gap_report.csv"]),
    ]),
    ("Stage 2 — ETL", [
        ("scripts/clean_nav_history.py",
         ["data/processed/clean_nav_history.csv",
          "data/processed/nav_quality_report.csv"]),
        ("scripts/clean_investor_transactions.py",
         ["data/processed/clean_investor_transactions.csv",
          "data/processed/investor_transaction_quality_report.csv"]),
        ("scripts/fund_master_analysis.py",
         ["data/processed/fund_master_summary.xlsx"]),
    ]),
    ("Stage 3 — Database Build", [
        ("scripts/load_to_sqlite.py",
         ["data/db/bluestock_mf.db",
          "data/processed/load_summary.csv"]),
    ]),
]


def log(message: str) -> None:
    """Print a timestamped progress line."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def fail(message: str) -> None:
    """Print a fatal error and exit non-zero (fail-fast)."""
    print(f"\n❌ PIPELINE FAILED: {message}", file=sys.stderr, flush=True)
    sys.exit(1)


def run_script(script: str, outputs: list[str]) -> float:
    """Run one script, verify its outputs, and return elapsed seconds."""
    if not (PROJECT_ROOT / script).exists():
        fail(f"script not found: {script}")

    log(f"  -> running {script}")
    start = time.perf_counter()
    result = subprocess.run([sys.executable, script], cwd=PROJECT_ROOT)
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        fail(f"{script} exited with code {result.returncode}")

    for rel in outputs:
        out = PROJECT_ROOT / rel
        if not out.exists() or out.stat().st_size == 0:
            fail(f"{script} did not produce expected output: {rel}")

    log(f"  OK  {script}  ({elapsed:0.1f}s, {len(outputs)} output(s) verified)")
    return elapsed


def main() -> None:
    print("=" * 64)
    print("Bluestock MF Analytics — data-engineering pipeline")
    print("=" * 64)
    log(f"Project root: {PROJECT_ROOT}")

    completed: list[str] = []
    overall_start = time.perf_counter()

    for title, steps in PIPELINE:
        print(f"\n{title}")
        print("-" * 64)
        for script, outputs in steps:
            run_script(script, outputs)
            completed.append(script)

    total = time.perf_counter() - overall_start

    print("\n" + "=" * 64)
    print("PIPELINE SUMMARY")
    print("=" * 64)
    for script in completed:
        print(f"  ✓ {script}")
    print("-" * 64)
    print(f"  {len(completed)} steps succeeded in {total:0.1f}s")
    print("\n✅ SUCCESS — database at data/db/bluestock_mf.db")


if __name__ == "__main__":
    main()
