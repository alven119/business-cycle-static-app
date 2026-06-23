"""Major-group phase evidence profiles for Phase 11."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Any

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
    safely_operationalizable_role_ids,
)
from business_cycle.shadow_model.phase_evidence_evaluators import (
    evaluate_phase_evidence,
)


@lru_cache(maxsize=None)
def build_major_group_phase_evidence_rows(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rule in build_book_phase_evidence_rule_rows():
        key = f"{rule['phase_or_layer']}::{rule['major_group_id']}"
        groups[key].append(rule)
    rows: list[dict[str, Any]] = []
    safe = safely_operationalizable_role_ids()
    for key, rules in sorted(groups.items()):
        phase, major_group_id = key.split("::", 1)
        outputs = [
            evaluate_phase_evidence(
                role_id=rule["role_id"],
                as_of=as_of,
                data_mode=data_mode,
            )
            if rule["role_id"] in safe
            else None
            for rule in rules
        ]
        evaluable = [row for row in outputs if row and row["phase_evidence_output_available"]]
        supportive = sum(row["supportive"] for row in evaluable)
        contradictory = sum(row["contradictory"] for row in evaluable)
        unavailable = len(rules) - len(evaluable)
        status = _group_status(
            required_count=len(rules),
            evaluable_count=len(evaluable),
            supportive_count=supportive,
            contradictory_count=contradictory,
        )
        rows.append(
            {
                "major_group_id": major_group_id,
                "phase_or_layer": phase,
                "required_core_role_ids": [rule["role_id"] for rule in rules],
                "supporting_role_ids": [],
                "evaluable_core_role_count": len(evaluable),
                "supportive_core_role_count": supportive,
                "contradictory_core_role_count": contradictory,
                "unavailable_core_role_count": unavailable,
                "unresolved_core_role_count": unavailable,
                "group_evidence_status": status,
                "evidence_completeness_ratio": len(evaluable) / len(rules),
                "candidate_input_eligible": False,
                "numeric_weight_used": False,
                "role_count_vote_used": False,
                "modern_extension_used_as_core": False,
                "supporting_role_used_as_core": False,
            }
        )
    return rows


def summarize_major_group_phase_evidence() -> dict[str, Any]:
    rows = build_major_group_phase_evidence_rows()
    partial = [
        row
        for row in rows
        if 0 < row["evaluable_core_role_count"] < len(row["required_core_role_ids"])
    ]
    complete = [
        row
        for row in rows
        if row["evaluable_core_role_count"] == len(row["required_core_role_ids"])
    ]
    return {
        "phase": "11",
        "major_group_phase_evidence_ready": True,
        "major_group_count": len(rows),
        "phase_evidence_partial_major_group_count": len(partial),
        "phase_evidence_complete_major_group_count": len(complete),
        "candidate_input_complete_major_group_count": 0,
        "group_promoted_with_missing_core_count": 0,
        "group_promoted_via_modern_extension_count": 0,
        "numeric_weight_aggregation_count": 0,
        "role_count_vote_count": 0,
        "rows": rows,
    }


def _group_status(
    *,
    required_count: int,
    evaluable_count: int,
    supportive_count: int,
    contradictory_count: int,
) -> str:
    if evaluable_count == 0:
        return "unavailable"
    if evaluable_count < required_count:
        return "incomplete"
    if supportive_count and contradictory_count:
        return "mixed"
    if supportive_count:
        return "supportive"
    if contradictory_count:
        return "contradictory"
    return "neutral"
