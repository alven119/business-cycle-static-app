"""Phase 15 economic validation protocol preregistration closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase14_non_emitting_decision_runtime_closure import (
    summarize_phase14_non_emitting_decision_runtime_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_validation_protocol_freeze import (
    summarize_shadow_validation_protocol_freeze,
)
from business_cycle.audits.validation_readiness import summarize_validation_readiness
from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)


DEFAULT_PHASE15_CLOSURE_PATH = Path(
    "specs/audits/phase15_validation_protocol_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_validation_protocol_preregistered_no_validation_execution"
)


def summarize_phase15_validation_protocol_closure(
    path: str | Path = DEFAULT_PHASE15_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    protocol = summarize_economic_validation_protocol()
    readiness = summarize_validation_readiness()
    freeze = summarize_shadow_validation_protocol_freeze()
    phase14 = summarize_phase14_non_emitting_decision_runtime_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "15",
        "phase_id": 15,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W7_DATA_LINEAGE",
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
            "W14_PROSPECTIVE_MONITORING",
        ],
        "deferred_capability_gaps": [
            "historical_accuracy_validation_not_started",
            "economic_validation_not_started",
            "prospective_validation_not_started",
            "holdout_not_registered",
            "validation_metrics_disabled",
        ],
        "semantic_drift_count": 0,
        "economic_validation_protocol_ready": protocol[
            "economic_validation_protocol_ready"
        ],
        "validation_readiness_registry_ready": readiness[
            "validation_readiness_registry_ready"
        ],
        "validation_layer_count": protocol["validation_layer_count"],
        "retrospective_diagnostic_distinguished_from_validation": protocol[
            "retrospective_diagnostic_distinguished_from_validation"
        ],
        "historical_accuracy_validation_not_started": protocol[
            "historical_accuracy_validation_not_started"
        ],
        "economic_validation_not_started": protocol[
            "economic_validation_not_started"
        ],
        "prospective_validation_not_started": protocol[
            "prospective_validation_not_started"
        ],
        "holdout_registered": protocol["holdout_registered"],
        "metric_computation_enabled": protocol["metric_computation_enabled"],
        "backtest_execution_enabled": protocol["backtest_execution_enabled"],
        "candidate_selection_enabled": protocol["candidate_selection_enabled"],
        "candidate_phase_emitted": protocol["candidate_phase_emitted"],
        "current_phase_emitted": protocol["current_phase_emitted"],
        "production_behavior_change_count": readiness[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": protocol[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": protocol[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": protocol["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": protocol[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": protocol["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha11_freeze_hash_valid": freeze["alpha11_freeze_hash_valid"],
        "alpha10_parent_preserved": freeze["alpha10_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": "not_started",
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 16,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase15_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase15_preregisters_validation_protocol_without_execution"
        ),
        "protocol": protocol,
        "readiness": readiness,
        "freeze": freeze,
        "phase14_closure": phase14,
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
        summary["validation_layer_count"] >= 5
        and summary["semantic_drift_count"] == 0
        and summary["freeze"]["validation_protocol_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase14_closure"]["result"] == "passed"
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
        "phase15_validation_protocol_closure"
    ]["expected"]
