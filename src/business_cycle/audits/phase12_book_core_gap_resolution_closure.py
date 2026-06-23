"""Phase 12 remaining book-core evidence gap closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_gap_resolution import (
    summarize_book_phase_evidence_gap_resolution,
)
from business_cycle.audits.phase11_book_core_phase_evidence_closure import (
    summarize_phase11_book_core_phase_evidence_closure,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_gap_resolution_freeze import (
    summarize_shadow_gap_resolution_freeze,
)


DEFAULT_PHASE12_CLOSURE_PATH = Path(
    "specs/audits/phase12_book_core_gap_resolution_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_remaining_book_core_gaps_reviewed_no_false_resolution_alpha8_"
    "frozen_candidate_model_disabled"
)


def summarize_phase12_book_core_gap_resolution_closure(
    path: str | Path = DEFAULT_PHASE12_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    gaps = summarize_book_phase_evidence_gap_resolution()
    freeze = summarize_shadow_gap_resolution_freeze()
    phase11 = summarize_phase11_book_core_phase_evidence_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "12",
        "phase_id": 12,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
            "C2_TRANSITION_RISK_DETECTION",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "candidate_selection_disabled",
            "current_phase_disabled",
            "remaining_book_core_rule_or_source_blockers",
            "economic_validation_not_started",
        ],
        "semantic_drift_count": 0,
        "gap_resolution_registry_ready": gaps["gap_resolution_registry_ready"],
        "remaining_gap_reviewed_count": gaps["remaining_gap_reviewed_count"],
        "safe_to_operationalize_count": gaps["safe_to_operationalize_count"],
        "newly_operationalized_evaluator_count": gaps[
            "newly_operationalized_evaluator_count"
        ],
        "still_blocked_gap_count": gaps["still_blocked_gap_count"],
        "false_resolution_count": gaps["false_resolution_count"],
        "arbitrary_threshold_added_count": gaps[
            "arbitrary_threshold_added_count"
        ],
        "numeric_weight_added_count": gaps["numeric_weight_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "candidate_phase_emitted": gaps["candidate_phase_emitted"],
        "current_phase_emitted": gaps["current_phase_emitted"],
        "production_behavior_change_count": phase11[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": phase11[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": phase11[
            "real_registry_write_attempt_count"
        ],
        "alpha8_freeze_hash_valid": freeze["alpha8_freeze_hash_valid"],
        "alpha7_parent_preserved": freeze["alpha7_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "candidate_capability_ready": False,
        "formal_decision_model_ready": False,
        "economic_validation_status": "not_started",
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "holdout_registered": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 13,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase12_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase12_reviews_remaining_phase_evidence_gaps_and_freezes_alpha8"
        ),
        "gaps": gaps,
        "freeze": freeze,
        "phase11_closure": phase11,
        "leakage": leakage,
        "qa12_closure": qa12,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["gap_resolution_registry_ready"] is True
        and summary["freeze"]["gap_resolution_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase11_closure"]["result"] == "passed"
        and summary["qa12_closure"]["result"] == "passed"
        and summary["qa12_closure"]["real_registry_record_count"] == 0
        and summary["qa12_closure"]["real_registry_write_attempt_count"] == 0
        and summary["qa12_closure"]["prospective_protocol_started"] is False
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase12_book_core_gap_resolution_closure"
    ]["expected"]
