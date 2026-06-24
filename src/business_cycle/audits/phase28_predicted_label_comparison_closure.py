"""Phase 28 predicted-label comparison closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase27_predicted_label_artifact_closure import (
    summarize_phase27_predicted_label_artifact_closure,
)
from business_cycle.audits.predicted_label_comparison_readiness import (
    summarize_predicted_label_comparison_readiness,
)
from business_cycle.audits.shadow_predicted_label_comparison_freeze import (
    summarize_shadow_predicted_label_comparison_freeze,
)


DEFAULT_PHASE28_CLOSURE_PATH = Path(
    "specs/audits/phase28_predicted_label_comparison_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_predicted_label_comparison_artifacts_generated_no_accuracy_or_performance_metrics"
)


def summarize_phase28_predicted_label_comparison_closure(
    path: str | Path = DEFAULT_PHASE28_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    readiness = summarize_predicted_label_comparison_readiness()
    freeze = summarize_shadow_predicted_label_comparison_freeze()
    phase27 = summarize_phase27_predicted_label_artifact_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "28",
        "phase_id": 28,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W6_HISTORICAL_REPLAY",
            "W7_DATA_LINEAGE",
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "historical_accuracy_not_computed",
            "economic_performance_not_computed",
            "candidate_model_disabled",
            "production_dashboard_not_wired",
        ],
        "semantic_drift_count": 0,
        "predicted_label_comparison_artifact_contract_ready": readiness[
            "predicted_label_comparison_artifact_contract_ready"
        ],
        "predicted_label_comparison_generator_ready": readiness[
            "predicted_label_comparison_generator_ready"
        ],
        "predicted_label_comparison_readiness_ready": readiness[
            "predicted_label_comparison_readiness_ready"
        ],
        "scenario_count": readiness["scenario_count"],
        "predicted_label_artifact_count": readiness[
            "predicted_label_artifact_count"
        ],
        "label_comparison_artifact_count": readiness[
            "label_comparison_artifact_count"
        ],
        "label_comparison_executed": readiness["label_comparison_executed"],
        "predicted_label_provenance_verified_count": readiness[
            "predicted_label_provenance_verified_count"
        ],
        "historical_label_provenance_verified_count": readiness[
            "historical_label_provenance_verified_count"
        ],
        "mapping_contract_hash_verified": readiness[
            "mapping_contract_hash_verified"
        ],
        "label_used_by_runtime_count": readiness["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": readiness[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": readiness[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": readiness["metric_computation_enabled"],
        "backtest_execution_enabled": readiness["backtest_execution_enabled"],
        "candidate_phase_emitted": readiness["candidate_phase_emitted"],
        "current_phase_emitted": readiness["current_phase_emitted"],
        "prohibited_artifact_field_count": readiness[
            "prohibited_artifact_field_count"
        ],
        "production_behavior_change_count": readiness[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": readiness[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": readiness[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": readiness["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": readiness[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": readiness["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha24_freeze_hash_valid": freeze["alpha24_freeze_hash_valid"],
        "alpha23_parent_preserved": freeze["alpha23_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "predicted_label_comparison_artifacts_generated_no_accuracy_or_performance_metrics"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 29,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase28_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase28_materializes_predicted_label_comparison_without_metrics"
        ),
        "readiness": readiness,
        "freeze": freeze,
        "phase27_closure": phase27,
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
        and summary["readiness"]["predicted_label_comparison_readiness_ready"]
        is True
        and summary["freeze"]["predicted_label_comparison_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase27_closure"]["result"] == "passed"
        and summary["phase27_closure"]["prospective_registry_record_count"] == 0
        and summary["phase27_closure"]["real_registry_write_attempt_count"] == 0
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase28_predicted_label_comparison_closure"
    ]["expected"]
