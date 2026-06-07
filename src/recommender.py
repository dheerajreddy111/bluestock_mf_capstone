"""Fund recommendation engine (Day 6, Section 5).

Serves the Top-3 Sharpe-ranked funds for a given risk profile from the
recommendations table produced by ``notebooks/05_advanced_analytics.ipynb``
(``data/processed/fund_recommendations.csv``).

Risk profiles (built from fund-master ``sub_category``):
    LOW RISK       : Liquid, Short Duration, Gilt
    MODERATE RISK  : Large Cap, Flexi Cap, Index
    HIGH RISK      : Mid Cap, Small Cap

Example
-------
>>> from src.recommender import recommend
>>> recommend("moderate")          # case/alias tolerant
        risk_profile  recommendation_rank                                    scheme_name category  sharpe_ratio
0  MODERATE RISK                    1  Mirae Asset Large Cap Fund - Regular - Growth   Equity        1.0682
...
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# --- Resolve the recommendations file relative to the repo root ---
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
RECOMMENDATIONS_PATH = _PROJECT_ROOT / "data" / "processed" / "fund_recommendations.csv"

# Accept friendly aliases -> canonical profile label used in the data
_PROFILE_ALIASES = {
    "low": "LOW RISK",
    "low risk": "LOW RISK",
    "moderate": "MODERATE RISK",
    "moderate risk": "MODERATE RISK",
    "medium": "MODERATE RISK",
    "high": "HIGH RISK",
    "high risk": "HIGH RISK",
}

# Columns returned to the caller (in order)
_DISPLAY_COLS = [
    "risk_profile",
    "recommendation_rank",
    "scheme_name",
    "category",
    "sharpe_ratio",
]


def _normalize(risk_profile: str) -> str:
    """Map a user-supplied profile string to the canonical label."""
    if not isinstance(risk_profile, str):
        raise TypeError(f"risk_profile must be a string, got {type(risk_profile).__name__}")
    key = risk_profile.strip().lower()
    if key not in _PROFILE_ALIASES:
        valid = sorted(set(_PROFILE_ALIASES.values()))
        raise ValueError(
            f"Unknown risk_profile {risk_profile!r}. "
            f"Use one of {valid} (aliases: low / moderate / high)."
        )
    return _PROFILE_ALIASES[key]


def recommend(risk_profile: str, path: str | Path = RECOMMENDATIONS_PATH) -> pd.DataFrame:
    """Return the Top-3 recommended funds for ``risk_profile``.

    Parameters
    ----------
    risk_profile : str
        One of "LOW RISK", "MODERATE RISK", "HIGH RISK" (case-insensitive;
        aliases "low"/"moderate"/"high"/"medium" are accepted).
    path : str | Path, optional
        Location of ``fund_recommendations.csv``. Defaults to the file under
        ``data/processed/``.

    Returns
    -------
    pandas.DataFrame
        Up to three rows ordered by ``recommendation_rank`` (best Sharpe first),
        with columns: risk_profile, recommendation_rank, scheme_name, category,
        sharpe_ratio.
    """
    profile = _normalize(risk_profile)

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Recommendations file not found: {path}. "
            "Run notebooks/05_advanced_analytics.ipynb Section 5 to generate it."
        )

    recs = pd.read_csv(path)
    out = (
        recs[recs["risk_profile"] == profile]
        .sort_values("recommendation_rank")
        .loc[:, _DISPLAY_COLS]
        .reset_index(drop=True)
    )
    return out


if __name__ == "__main__":  # pragma: no cover - simple CLI demo
    for _profile in ("LOW RISK", "MODERATE RISK", "HIGH RISK"):
        print(f"\n=== {_profile} ===")
        print(recommend(_profile).to_string(index=False))
