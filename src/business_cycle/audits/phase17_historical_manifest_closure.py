"""Phase 17 historical validation manifest preregistration closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_validation_readiness import (
    summarize_historical_validation_readiness,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase16_validation_harness_closure import (
    summarize_phase16_validation_harness_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_historical_manifest_freeze import (
    summarize_shadow_historical_manifest_freeze,
)
from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


DEFAULT_PHASE17_CLOSURE_PATH = Path(
    "specs/audits/phase17_historical_manifest_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_historical_validation_manifest_preregistered_no_validation_execution"
)


def summarize_phase17_historical_manifest_closure(
    path: str | Path = DEFAULT_PHASE17_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    manifest = summarize_historical_validation_manifest()
    label_policy = summarize_validation_label_policy()
    readiness = summarize_historical_validation_readiness()
    freeze = summarize_shadow_historical_manifest_freeze()
    phase16 = summarize_phase16_validation_harness_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "17",
        "phase_id": 17,
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
            "historical_validation_not_executed",
            "metrics_not_registered_for_execution",
            "economic_validation_not_started",
            "holdout_not_registered",
        ],
        "semantic_drift_count": 0,
        "historical_validation_manifest_contract_ready": manifest[
            "historical_validation_manifest_contract_ready"
        ],
        "historical_validation_scenario_manifest_ready": manifest[
            "historical_validation_scenario_manifest_ready"
        ],
        "validation_label_policy_ready": label_policy[
            "validation_label_policy_ready"
        ],
        "historical_validation_readiness_ready": readiness[
            "historical_validation_readiness_ready"
        ],
        "scenario_count": manifest["scenario_count"],
        "point_in_time_requirement_present": manifest[
            "point_in_time_requirement_present"
        ],
        "label_provenance_complete": readiness["label_provenance_complete"],
        "label_runtime_usage_prohibited": readiness[
            "label_runtime_usage_prohibited"
        ],
        "no_tuning_after_manifest_rule_present": manifest[
            "no_tuning_after_manifest_rule_present"
        ],
        "real_historical_validation_executed": readiness[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": readiness[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": readiness[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": readiness["metric_computation_enabled"],
        "backtest_execution_enabled": readiness["backtest_execution_enabled"],
        "holdout_registered": readiness["holdout_registered"],
        "candidate_selection_enabled": readiness["candidate_selection_enabled"],
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
        "alpha13_freeze_hash_valid": freeze["alpha13_freeze_hash_valid"],
        "alpha12_parent_preserved": freeze["alpha12_parent_preserved"],
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
        "development_next_phase": 18,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase17_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase17_preregisters_historical_validation_manifest_without_execution"
        ),
        "manifest": manifest,
        "label_policy": label_policy,
        "readiness": readiness,
        "freeze": freeze,
        "phase16_closure": phase16,
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
        summary["scenario_count"] > 0
        and summary["semantic_drift_count"] == 0
        and summary["freeze"]["historical_manifest_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["manifest"]["scenario_execution_started_count"] == 0
        and summary["manifest"]["metric_or_backtest_count"] == 0
        and summary["manifest"]["candidate_or_current_phase_read_count"] == 0
        and summary["phase16_closure"]["result"] == "passed"
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
        "phase17_historical_manifest_closure"
    ]["expected"]
