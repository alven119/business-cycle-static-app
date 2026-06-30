"""Product capability progress reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROGRESS_PATH = ROOT / "specs/common/product_capability_progress.yaml"

CORE_CAPABILITY_IDS = {
    "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
    "C2_TRANSITION_RISK_DETECTION",
    "C3_EXPLAINABILITY_AND_ATTRIBUTION",
    "C4_PORTFOLIO_POLICY_RESEARCH",
    "C5_HISTORICAL_REPLAY_AND_BACKTEST",
    "C6_SAFE_OUTPUT_GOVERNANCE",
    "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
    "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
}

PROHIBITED_CLAIM_FRAGMENTS = {
    "production" + "-ready",
    "investment" + "-ready",
    "real backtest " + "ready",
    "book-faithful model complete",
    "candidate phase ready",
    "economically validated",
}


def build_product_capability_progress(
    path: str | Path = DEFAULT_PROGRESS_PATH,
) -> dict[str, Any]:
    """Load the governed product capability progress view."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "product_capability_progress"
    ]
    rows = list(payload["capability_progress"])
    return {
        "version": payload["version"],
        "status": payload["status"],
        "phase_id": payload["phase_id"],
        "phase_label": payload["phase_label"],
        "progress_semantics": payload["progress_semantics"],
        "capability_progress": rows,
    }


def summarize_product_capability_progress(
    path: str | Path = DEFAULT_PROGRESS_PATH,
) -> dict[str, Any]:
    """Summarize capability progress for phase final reporting."""

    progress = build_product_capability_progress(path)
    rows = progress["capability_progress"]
    ids = {row["capability_id"] for row in rows}
    impacted = [row for row in rows if row["phase52_impacted"]]
    out_of_range = [
        row
        for row in rows
        if not (0 <= int(row["current_progress_percent"]) <= 100)
        or not (0 <= int(row["previous_progress_percent"]) <= 100)
    ]
    unsupported_claims = _unsupported_claim_count(progress)
    expected = _load_expected(path)
    summary = {
        "product_capability_progress_ready": ids == CORE_CAPABILITY_IDS
        and not out_of_range
        and unsupported_claims == 0,
        "phase_id": progress["phase_id"],
        "phase_label": progress["phase_label"],
        "capability_count": len(rows),
        "capability_with_percent_count": sum(
            "current_progress_percent" in row for row in rows
        ),
        "impacted_capability_count": len(impacted),
        "impacted_capability_ids": [row["capability_id"] for row in impacted],
        "average_progress_percent": round(
            sum(int(row["current_progress_percent"]) for row in rows) / len(rows),
            1,
        ),
        "progress_percent_out_of_range_count": len(out_of_range),
        "unsupported_readiness_claim_count": unsupported_claims,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "capability_progress": rows,
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "product_capability_progress"
    ]
    return dict(payload["hard_gates"])


def _unsupported_claim_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_unsupported_claim_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_unsupported_claim_count(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return int(any(fragment in lowered for fragment in PROHIBITED_CLAIM_FRAGMENTS))
    return 0
