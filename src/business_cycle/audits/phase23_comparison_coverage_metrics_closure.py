"""Phase 23 comparison-coverage metrics closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_comparison_coverage_metrics import (
    summarize_historical_comparison_coverage_metrics_registry,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase22_label_comparison_artifact_closure import (
    summarize_phase22_label_comparison_artifact_closure,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.audits.shadow_comparison_coverage_metrics_freeze import (
    summarize_shadow_comparison_coverage_metrics_freeze,
)


DEFAULT_PHASE23_CLOSURE_PATH = Path(
    "specs/audits/phase23_comparison_coverage_metrics_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_comparison_coverage_metrics_computed_no_accuracy_or_performance"
)


def summarize_phase23_comparison_coverage_metrics_closure(
    path: str | Path = DEFAULT_PHASE23_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    registry = summarize_historical_comparison_coverage_metrics_registry()
    freeze = summarize_shadow_comparison_coverage_metrics_freeze()
    phase22 = summarize_phase22_label_comparison_artifact_closure()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "23",
        "phase_id": 23,
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
            "holdout_not_registered",
            "candidate_model_disabled",
            "production_dashboard_not_wired",
        ],
        "semantic_drift_count": 0,
        "comparison_coverage_metrics_contract_ready": registry[
            "comparison_coverage_metrics_contract_ready"
        ],
        "comparison_coverage_metrics_runtime_ready": registry[
            "comparison_coverage_metrics_runtime_ready"
        ],
        "comparison_coverage_metrics_registry_ready": registry[
            "comparison_coverage_metrics_registry_ready"
        ],
        "scenario_count": registry["scenario_count"],
        "label_comparison_artifact_count": registry[
            "label_comparison_artifact_count"
        ],
        "label_provenance_verified_count": registry[
            "label_provenance_verified_count"
        ],
        "label_used_by_runtime_count": registry["label_used_by_runtime_count"],
        "comparison_coverage_metric_count": registry[
            "comparison_coverage_metric_count"
        ],
        "metric_computation_enabled": registry["metric_computation_enabled"],
        "metric_computation_scope": registry["metric_computation_scope"],
        "historical_accuracy_metric_count": registry[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": registry[
            "economic_performance_metric_count"
        ],
        "prohibited_metric_field_count": registry[
            "prohibited_metric_field_count"
        ],
        "predicted_label_output_count": registry["predicted_label_output_count"],
        "candidate_phase_emitted": registry["candidate_phase_emitted"],
        "current_phase_emitted": registry["current_phase_emitted"],
        "backtest_execution_enabled": registry["backtest_execution_enabled"],
        "holdout_registered": registry["holdout_registered"],
        "production_behavior_change_count": registry[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": registry[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": registry[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": registry["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": registry[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": registry["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "alpha19_freeze_hash_valid": freeze["alpha19_freeze_hash_valid"],
        "alpha18_parent_preserved": freeze["alpha18_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "comparison_coverage_metrics_computed_no_accuracy"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 24,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase23_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase23_computes_coverage_only_metrics_without_accuracy_or_performance"
        ),
        "metrics_registry": registry,
        "freeze": freeze,
        "phase22_closure": phase22,
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
        and summary["metrics_registry"][
            "comparison_coverage_metrics_registry_ready"
        ]
        is True
        and summary["freeze"]["comparison_coverage_metrics_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase22_closure"]["result"] == "passed"
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
        "phase23_comparison_coverage_metrics_closure"
    ]["expected"]
