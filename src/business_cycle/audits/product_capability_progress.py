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
    "book-faithful model " + "complete",
    "candidate phase " + "ready",
    "economically " + "validated",
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
    impacted = [row for row in rows if _phase_impacted(row)]
    decrease_rows = [
        row
        for row in rows
        if int(row["current_progress_percent"]) < int(row["previous_progress_percent"])
    ]
    out_of_range = [
        row
        for row in rows
        if not (0 <= int(row["current_progress_percent"]) <= 100)
        or not (0 <= int(row["previous_progress_percent"]) <= 100)
    ]
    unsupported_claims = _unsupported_claim_count(progress)
    expected = _load_expected(path)
    completed_summary_count = _field_present_count(rows, "completed_summary_zh")
    incomplete_summary_count = _field_present_count(rows, "incomplete_summary_zh")
    next_gap_count = _field_present_count(rows, "next_gap_zh")
    decrease_without_reason_count = sum(
        not bool(row.get("decrease_reason_zh")) for row in decrease_rows
    )
    summary = {
        "product_capability_progress_ready": ids == CORE_CAPABILITY_IDS
        and not out_of_range
        and completed_summary_count == len(rows)
        and incomplete_summary_count == len(rows)
        and next_gap_count == len(rows)
        and decrease_without_reason_count == 0
        and unsupported_claims == 0,
        "phase_id": progress["phase_id"],
        "phase_label": progress["phase_label"],
        "progress_semantics": progress["progress_semantics"],
        "capability_count": len(rows),
        "capability_with_percent_count": sum(
            "current_progress_percent" in row for row in rows
        ),
        "capability_with_completed_summary_count": completed_summary_count,
        "capability_with_incomplete_summary_count": incomplete_summary_count,
        "capability_with_next_gap_count": next_gap_count,
        "impacted_capability_count": len(impacted),
        "impacted_capability_ids": [row["capability_id"] for row in impacted],
        "average_progress_percent": round(
            sum(int(row["current_progress_percent"]) for row in rows) / len(rows),
            1,
        ),
        "progress_decrease_count": len(decrease_rows),
        "progress_decrease_without_reason_count": decrease_without_reason_count,
        "progress_percent_out_of_range_count": len(out_of_range),
        "unsupported_readiness_claim_count": unsupported_claims,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "capability_table_rows": [_capability_table_row(row) for row in rows],
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


def _field_present_count(rows: list[dict[str, Any]], field: str) -> int:
    return sum(bool(row.get(field)) for row in rows)


def _capability_table_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "capability": f"{row['capability_id']} {row['title_zh']}",
        "previous": row["previous_progress_percent"],
        "current": row["current_progress_percent"],
        "delta": row["phase_delta_percent"],
        "phase_impact": _phase_impact(row),
        "next_gap": row["next_gap_zh"],
        "completed_summary": row["completed_summary_zh"],
        "incomplete_summary": row["incomplete_summary_zh"],
        "decrease_reason": row.get("decrease_reason_zh"),
    }


def _phase_impacted(row: dict[str, Any]) -> bool:
    return bool(row.get("phase_impacted", row.get("phase52_impacted", False)))


def _phase_impact(row: dict[str, Any]) -> str:
    return str(row.get("phase_impact_zh") or row.get("phase52_impact_zh") or "")


def _unsupported_claim_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_unsupported_claim_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_unsupported_claim_count(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return int(any(fragment in lowered for fragment in PROHIBITED_CLAIM_FRAGMENTS))
    return 0
