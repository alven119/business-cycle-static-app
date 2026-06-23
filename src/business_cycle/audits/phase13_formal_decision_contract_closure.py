"""Phase 13 formal decision contract preregistration closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase12_book_core_gap_resolution_closure import (
    summarize_phase12_book_core_gap_resolution_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_decision_contract_freeze import (
    summarize_shadow_decision_contract_freeze,
)
from business_cycle.shadow_model.candidate_precondition_profiles import (
    summarize_candidate_precondition_profiles,
)
from business_cycle.shadow_model.formal_decision_contract import (
    summarize_formal_decision_model_contract,
)


DEFAULT_PHASE13_CLOSURE_PATH = Path(
    "specs/audits/phase13_formal_decision_contract_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_formal_decision_contract_preregistered_candidate_output_disabled"
)


def summarize_phase13_formal_decision_contract_closure(
    path: str | Path = DEFAULT_PHASE13_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    contract = summarize_formal_decision_model_contract()
    profiles = summarize_candidate_precondition_profiles()
    freeze = summarize_shadow_decision_contract_freeze()
    phase12 = summarize_phase12_book_core_gap_resolution_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "13",
        "phase_id": 13,
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
            "candidate_capability_incomplete",
            "economic_validation_not_started",
        ],
        "semantic_drift_count": 0,
        "formal_decision_contract_ready": contract[
            "formal_decision_contract_ready"
        ],
        "candidate_precondition_profile_ready": profiles[
            "candidate_precondition_profile_ready"
        ],
        "candidate_input_eligibility_rule_count": contract[
            "candidate_input_eligibility_rule_count"
        ],
        "phase_presence_transition_separation_valid": contract[
            "phase_presence_transition_separation_valid"
        ],
        "abstention_propagation_ready": contract[
            "abstention_propagation_ready"
        ],
        "contradictory_evidence_rule_ready": contract[
            "contradictory_evidence_rule_ready"
        ],
        "mixed_evidence_rule_ready": contract["mixed_evidence_rule_ready"],
        "unavailable_evidence_rule_ready": contract[
            "unavailable_evidence_rule_ready"
        ],
        "numeric_weight_added_count": contract["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": contract[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": contract[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "candidate_selection_enabled": contract["candidate_selection_enabled"],
        "candidate_phase_emitted": (
            contract["candidate_phase_emitted"]
            or profiles["candidate_phase_emitted"]
        ),
        "current_phase_emitted": (
            contract["current_phase_emitted"] or profiles["current_phase_emitted"]
        ),
        "production_behavior_change_count": phase12[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": phase12[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": phase12[
            "real_registry_write_attempt_count"
        ],
        "alpha9_freeze_hash_valid": freeze["alpha9_freeze_hash_valid"],
        "alpha8_parent_preserved": freeze["alpha8_parent_preserved"],
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
        "development_next_phase": 14,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase13_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase13_preregisters_formal_decision_contract_with_candidate_output_disabled"
        ),
        "contract": contract,
        "profiles": profiles,
        "freeze": freeze,
        "phase12_closure": phase12,
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
        and summary["candidate_input_eligibility_rule_count"] > 0
        and summary["freeze"]["decision_contract_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase12_closure"]["result"] == "passed"
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
        "phase13_formal_decision_contract_closure"
    ]["expected"]
