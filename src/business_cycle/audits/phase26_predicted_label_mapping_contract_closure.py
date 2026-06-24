"""Phase 26 predicted-label mapping contract closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.offline_predicted_label_mapping_readiness import (
    summarize_offline_predicted_label_mapping_readiness,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase25_research_decision_output_closure import (
    summarize_phase25_research_decision_output_closure,
)
from business_cycle.audits.shadow_predicted_label_mapping_contract_freeze import (
    summarize_shadow_predicted_label_mapping_contract_freeze,
)


DEFAULT_PHASE26_CLOSURE_PATH = Path(
    "specs/audits/phase26_predicted_label_mapping_contract_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = "closed_predicted_label_mapping_preregistered_no_emission_or_metrics"


def summarize_phase26_predicted_label_mapping_contract_closure(
    path: str | Path = DEFAULT_PHASE26_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    readiness = summarize_offline_predicted_label_mapping_readiness()
    freeze = summarize_shadow_predicted_label_mapping_contract_freeze()
    phase25 = summarize_phase25_research_decision_output_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "26",
        "phase_id": 26,
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
            "predicted_label_artifacts_not_emitted",
            "label_comparison_not_executed",
            "historical_accuracy_not_computed",
            "economic_performance_not_computed",
            "candidate_model_disabled",
            "production_dashboard_not_wired",
        ],
        "semantic_drift_count": 0,
        "predicted_label_mapping_contract_ready": readiness[
            "predicted_label_mapping_contract_ready"
        ],
        "predicted_label_mapping_readiness_ready": readiness[
            "predicted_label_mapping_readiness_ready"
        ],
        "research_decision_state_taxonomy_ready": readiness[
            "research_decision_state_taxonomy_ready"
        ],
        "offline_predicted_label_taxonomy_ready": readiness[
            "offline_predicted_label_taxonomy_ready"
        ],
        "mapping_rule_count": readiness["mapping_rule_count"],
        "predicted_label_output_count": readiness["predicted_label_output_count"],
        "predicted_label_artifact_count": readiness[
            "predicted_label_artifact_count"
        ],
        "label_comparison_executed": readiness["label_comparison_executed"],
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
        "alpha22_freeze_hash_valid": freeze["alpha22_freeze_hash_valid"],
        "alpha21_parent_preserved": freeze["alpha21_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "predicted_label_mapping_preregistered_no_emission"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 27,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase26_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase26_preregisters_offline_predicted_label_mapping_without_emission"
        ),
        "readiness": readiness,
        "freeze": freeze,
        "phase25_closure": phase25,
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
        and summary["mapping_rule_count"] > 0
        and summary["readiness"]["predicted_label_mapping_readiness_ready"] is True
        and summary["freeze"]["predicted_label_mapping_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase25_closure"]["result"] == "passed"
        and summary["phase25_closure"]["prospective_registry_record_count"] == 0
        and summary["phase25_closure"]["real_registry_write_attempt_count"] == 0
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase26_predicted_label_mapping_contract_closure"
    ]["expected"]
