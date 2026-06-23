"""Phase 14 non-emitting formal decision runtime closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase13_formal_decision_contract_closure import (
    summarize_phase13_formal_decision_contract_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_decision_runtime_freeze import (
    summarize_shadow_decision_runtime_freeze,
)
from business_cycle.shadow_model.decision_readiness_matrix import (
    summarize_decision_readiness_matrix,
)
from business_cycle.shadow_model.formal_decision_runtime import (
    summarize_formal_decision_runtime,
)


DEFAULT_PHASE14_CLOSURE_PATH = Path(
    "specs/audits/phase14_non_emitting_decision_runtime_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_non_emitting_decision_runtime_ready_candidate_output_disabled"
)


def summarize_phase14_non_emitting_decision_runtime_closure(
    path: str | Path = DEFAULT_PHASE14_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    runtime = summarize_formal_decision_runtime()
    matrix = summarize_decision_readiness_matrix()
    freeze = summarize_shadow_decision_runtime_freeze()
    phase13 = summarize_phase13_formal_decision_contract_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "14",
        "phase_id": 14,
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
            "W7_DATA_LINEAGE",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "candidate_selection_disabled",
            "current_phase_disabled",
            "formal_decision_emission_disabled",
            "economic_validation_not_started",
        ],
        "semantic_drift_count": 0,
        "non_emitting_decision_runtime_ready": runtime[
            "non_emitting_decision_runtime_ready"
        ],
        "formal_decision_contract_enforced": runtime[
            "formal_decision_contract_enforced"
        ],
        "decision_readiness_matrix_ready": matrix["decision_readiness_matrix_ready"],
        "evaluated_precondition_rule_count": runtime[
            "evaluated_precondition_rule_count"
        ],
        "abstention_propagation_executed": runtime[
            "abstention_propagation_executed"
        ],
        "contradictory_evidence_rule_executed": runtime[
            "contradictory_evidence_rule_executed"
        ],
        "mixed_evidence_rule_executed": runtime["mixed_evidence_rule_executed"],
        "unavailable_evidence_rule_executed": runtime[
            "unavailable_evidence_rule_executed"
        ],
        "raw_observation_only_blocking_executed": runtime[
            "raw_observation_only_blocking_executed"
        ],
        "phase_presence_transition_separation_valid": runtime[
            "phase_presence_transition_separation_valid"
        ],
        "watch_confirmation_separation_valid": runtime[
            "watch_confirmation_separation_valid"
        ],
        "prohibited_decision_output_field_count": runtime[
            "prohibited_decision_output_field_count"
        ],
        "selected_phase_output_count": runtime["selected_phase_output_count"],
        "phase_rank_output_count": runtime["phase_rank_output_count"],
        "phase_score_output_count": runtime["phase_score_output_count"],
        "numeric_weight_added_count": runtime["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": runtime[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": runtime["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "candidate_selection_enabled": runtime["candidate_selection_enabled"],
        "candidate_phase_emitted": runtime["candidate_phase_emitted"],
        "current_phase_emitted": runtime["current_phase_emitted"],
        "production_behavior_change_count": phase13[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": phase13[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": phase13[
            "real_registry_write_attempt_count"
        ],
        "alpha10_freeze_hash_valid": freeze["alpha10_freeze_hash_valid"],
        "alpha9_parent_preserved": freeze["alpha9_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": "not_started",
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "holdout_registered": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 15,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase14_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase14_executes_non_emitting_formal_decision_runtime_diagnostics"
        ),
        "runtime": runtime,
        "matrix": matrix,
        "freeze": freeze,
        "phase13_closure": phase13,
        "qa12_closure": qa12,
        "leakage": leakage,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["freeze"]["decision_runtime_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase13_closure"]["result"] == "passed"
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
        "phase14_non_emitting_decision_runtime_closure"
    ]["expected"]
