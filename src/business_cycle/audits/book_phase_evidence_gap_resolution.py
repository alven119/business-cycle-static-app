"""Phase 12 remaining book-core phase-evidence gap resolution registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)


DEFAULT_GAP_RESOLUTION_PATH = Path(
    "specs/audits/book_phase_evidence_gap_resolution_registry.yaml"
)

REMAINING_PHASE11_GAP_IDS = {
    "boom_consumer_confidence",
    "growth_adp_employment",
    "growth_real_disposable_income_vs_consumption",
    "growth_sustainable_inflation_interpretation",
    "recovery_weekly_claim_noise_filter",
    "growth_personal_saving_rate",
    "growth_core_cpi",
    "growth_core_pce",
    "trough_policy_financial_not_sufficient_alone",
}


def load_book_phase_evidence_gap_resolution_registry(
    path: str | Path = DEFAULT_GAP_RESOLUTION_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_phase_evidence_gap_resolution_registry"
    ]


def build_book_phase_evidence_gap_resolution_rows(
    path: str | Path = DEFAULT_GAP_RESOLUTION_PATH,
) -> list[dict[str, Any]]:
    return list(load_book_phase_evidence_gap_resolution_registry(path)["gaps"])


def summarize_book_phase_evidence_gap_resolution(
    path: str | Path = DEFAULT_GAP_RESOLUTION_PATH,
) -> dict[str, Any]:
    registry = load_book_phase_evidence_gap_resolution_registry(path)
    rows = build_book_phase_evidence_gap_resolution_rows(path)
    role_ids = [row["role_id"] for row in rows]
    role_id_set = set(role_ids)
    phase11_rows = {
        row["role_id"]: row for row in build_book_phase_evidence_rule_rows()
    }
    duplicate_count = len(role_ids) - len(role_id_set)
    missing_expected = REMAINING_PHASE11_GAP_IDS - role_id_set
    unexpected = role_id_set - REMAINING_PHASE11_GAP_IDS
    policy = registry["resolution_policy"]
    counters = _resolution_counters(rows)
    false_resolution_rows = [
        row for row in rows if _is_false_resolution(row, policy)
    ]
    phase11_gap_mismatch = [
        row
        for row in rows
        if phase11_rows.get(row["role_id"], {}).get("evaluator_status")
        != row["phase11_status"]
    ]
    summary = {
        "phase": "12",
        "registry_id": registry["registry_id"],
        "parent_freeze_id": registry["parent_freeze_id"],
        "remaining_gap_reviewed_count": len(rows),
        "expected_remaining_gap_count": len(REMAINING_PHASE11_GAP_IDS),
        "missing_expected_gap_count": len(missing_expected),
        "unexpected_gap_count": len(unexpected),
        "duplicate_gap_count": duplicate_count,
        "phase11_gap_status_mismatch_count": len(phase11_gap_mismatch),
        "safe_to_operationalize_count": counters["safe_to_operationalize"],
        "newly_operationalized_evaluator_count": counters[
            "operational_evaluator_added"
        ],
        "still_blocked_gap_count": sum(
            row["resolution_status"].startswith("retained") for row in rows
        ),
        "false_resolution_count": len(false_resolution_rows),
        "arbitrary_threshold_added_count": counters["numeric_threshold_added"],
        "numeric_weight_added_count": counters["numeric_weight_added"],
        "historical_tuning_leakage_count": counters["historical_tuning_used"],
        "prohibited_substitution_count": counters["prohibited_substitution_used"],
        "candidate_selection_eligible_count": counters[
            "candidate_selection_eligible"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "phase_support_added_count": counters["phase_support_added"],
        "book_semantics_complete_count": sum(
            row["book_semantics_status"] == "complete" for row in rows
        ),
        "source_blocker_count": sum(
            row["blocker_class"]
            in {"no_public_official_equivalent", "proprietary_access_required"}
            for row in rows
        ),
        "rule_semantics_blocker_count": sum(
            row["blocker_class"]
            in {
                "composite_rule_semantics_incomplete",
                "qualitative_rule_semantics_incomplete",
                "phase_support_rule_incomplete",
                "component_not_composite_phase_evidence",
            }
            for row in rows
        ),
        "supporting_only_blocker_count": counters["supporting_only_not_confirmation"],
        "smoothing_only_blocker_count": counters["smoothing_not_phase_evidence"],
        "resolution_status_counts": dict(
            sorted(Counter(row["resolution_status"] for row in rows).items())
        ),
        "blocker_class_counts": dict(
            sorted(Counter(row["blocker_class"] for row in rows).items())
        ),
        "rows": rows,
    }
    summary["gap_resolution_registry_ready"] = (
        summary["remaining_gap_reviewed_count"]
        == summary["expected_remaining_gap_count"]
        and summary["missing_expected_gap_count"] == 0
        and summary["unexpected_gap_count"] == 0
        and summary["duplicate_gap_count"] == 0
        and summary["phase11_gap_status_mismatch_count"] == 0
        and summary["false_resolution_count"] == 0
        and summary["arbitrary_threshold_added_count"] == 0
        and summary["numeric_weight_added_count"] == 0
        and summary["historical_tuning_leakage_count"] == 0
        and summary["prohibited_substitution_count"] == 0
        and summary["candidate_selection_eligible_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
    )
    return summary


def _resolution_counters(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        for key in (
            "safe_to_operationalize",
            "operational_evaluator_added",
            "phase_support_added",
            "candidate_selection_eligible",
            "numeric_threshold_added",
            "numeric_weight_added",
            "historical_tuning_used",
            "prohibited_substitution_used",
            "false_resolution_risk",
        ):
            counter[key] += int(row[key])
        counter[row["blocker_class"]] += 1
    return counter


def _is_false_resolution(row: dict[str, Any], policy: dict[str, Any]) -> bool:
    required_complete = (
        policy["require_book_semantics_complete"]
        and policy["require_source_complete"]
        and policy["require_transformation_complete"]
        and policy["require_temporal_rule_complete"]
        and policy["require_abstention_rule_complete"]
    )
    evaluator_added_without_safety = (
        row["operational_evaluator_added"] and not row["safe_to_operationalize"]
    )
    prohibited_enabled = (
        row["numeric_threshold_added"] and not policy["allow_arbitrary_threshold"]
    ) or (row["numeric_weight_added"] and not policy["allow_numeric_weight"])
    forbidden_output = row["candidate_selection_eligible"] or row[
        "current_phase_output_allowed"
    ]
    unresolved_but_operationalized = (
        row["resolution_status"] == "operationalized" and not required_complete
    )
    return bool(
        row["false_resolution_risk"]
        or evaluator_added_without_safety
        or prohibited_enabled
        or forbidden_output
        or unresolved_but_operationalized
    )
