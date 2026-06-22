"""QA11 major-group observation coverage audit."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)


def build_major_group_observation_rows() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in build_book_core_forward_data_gap_rows():
        grouped[f"{role['phase_or_layer']}::{role['major_group_id']}"].append(role)
    rows: list[dict[str, Any]] = []
    for group_key, roles in sorted(grouped.items()):
        phase, major_group_id = group_key.split("::", 1)
        required_count = len(roles)
        observable = sum(row["observation_evaluator_supported"] for row in roles)
        phase_evidence = sum(row["phase_evidence_evaluator_supported"] for row in roles)
        forward_ready = sum(
            row["forward_prospective_capture_status"]
            in {"ready", "ready_with_manual_capture"}
            for row in roles
        )
        unavailable = required_count - forward_ready
        access_blocked = sum(
            row["forward_prospective_capture_status"] == "blocked_access"
            for row in roles
        )
        source_blocked = sum(
            row["forward_prospective_capture_status"] == "blocked_source_identity"
            for row in roles
        )
        observation_status = _coverage_status(observable, required_count)
        phase_status = _coverage_status(phase_evidence, required_count)
        rows.append(
            {
                "major_group_id": major_group_id,
                "phase": phase,
                "required_core_role_count": required_count,
                "forward_capture_ready_role_count": forward_ready,
                "runtime_observable_role_count": observable,
                "phase_evidence_evaluable_role_count": phase_evidence,
                "unavailable_role_count": unavailable,
                "access_blocked_role_count": access_blocked,
                "source_blocked_role_count": source_blocked,
                "observation_monitoring_status": observation_status,
                "phase_evidence_status": phase_status
                if phase_evidence
                else "unavailable",
                "candidate_input_status": "incomplete",
                "modern_substitution_used": False,
                "missing_core_role_count": required_count - observable,
            }
        )
    return rows


def summarize_major_group_observation_coverage() -> dict[str, Any]:
    rows = build_major_group_observation_rows()
    ready = [
        row for row in rows if row["observation_monitoring_status"] == "ready"
    ]
    partial = [
        row for row in rows if row["observation_monitoring_status"] == "partial"
    ]
    blocked = [
        row for row in rows if row["observation_monitoring_status"] == "blocked"
    ]
    group_ready_with_missing = [
        row
        for row in ready
        if row["missing_core_role_count"] > 0
    ]
    return {
        "phase": "QA11",
        "major_group_observation_coverage_ready": True,
        "major_group_count": len(rows),
        "observation_ready_major_group_count": len(ready),
        "observation_partial_major_group_count": len(partial),
        "observation_blocked_major_group_count": len(blocked),
        "phase_evidence_evaluable_major_group_count": sum(
            row["phase_evidence_status"] == "evaluable" for row in rows
        ),
        "candidate_input_complete_major_group_count": sum(
            row["candidate_input_status"] == "complete" for row in rows
        ),
        "group_ready_via_modern_substitution_count": sum(
            row["modern_substitution_used"] for row in rows
        ),
        "group_ready_with_missing_core_role_count": len(group_ready_with_missing),
        "rows": rows,
    }


def _coverage_status(count: int, required: int) -> str:
    if count == required and required > 0:
        return "ready"
    if count > 0:
        return "partial"
    return "blocked"

