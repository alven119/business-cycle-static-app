"""Phase 29 research-only historical accuracy metric closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_accuracy_metric_readiness import (
    summarize_historical_accuracy_metric_readiness,
)
from business_cycle.audits.phase28_predicted_label_comparison_closure import (
    summarize_phase28_predicted_label_comparison_closure,
)
from business_cycle.audits.shadow_historical_accuracy_metrics_freeze import (
    summarize_shadow_historical_accuracy_metrics_freeze,
)


DEFAULT_PHASE29_CLOSURE_PATH = Path(
    "specs/audits/phase29_historical_accuracy_metrics_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_historical_accuracy_metrics_computed_research_only_no_economic_performance"
)


@lru_cache(maxsize=1)
def summarize_phase29_historical_accuracy_metrics_closure(
    path: str | Path = DEFAULT_PHASE29_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    readiness = summarize_historical_accuracy_metric_readiness()
    freeze = summarize_shadow_historical_accuracy_metrics_freeze()
    phase28 = summarize_phase28_predicted_label_comparison_closure()
    summary = {
        "phase": "29",
        "phase_id": 29,
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
            "economic performance metrics not computed",
            "portfolio backtest not executed",
            "candidate model disabled",
            "current phase disabled",
            "dashboard not production-wired",
        ],
        "semantic_drift_count": 0,
        "historical_accuracy_metric_artifact_contract_ready": readiness[
            "historical_accuracy_metric_artifact_contract_ready"
        ],
        "historical_accuracy_metric_runtime_ready": readiness[
            "historical_accuracy_metric_runtime_ready"
        ],
        "historical_accuracy_metric_readiness_ready": readiness[
            "historical_accuracy_metric_readiness_ready"
        ],
        "preregistered_metric_registry_used": readiness[
            "preregistered_metric_registry_used"
        ],
        "scenario_count": readiness["scenario_count"],
        "label_comparison_artifact_count": readiness[
            "label_comparison_artifact_count"
        ],
        "comparable_scenario_count": readiness["comparable_scenario_count"],
        "non_comparable_scenario_count": readiness[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": readiness["abstained_scenario_count"],
        "blocked_scenario_count": readiness["blocked_scenario_count"],
        "taxonomy_mismatch_count": readiness["taxonomy_mismatch_count"],
        "historical_accuracy_metric_count": readiness[
            "historical_accuracy_metric_count"
        ],
        "computed_metric_count": readiness["computed_metric_count"],
        "skipped_metric_count": readiness["skipped_metric_count"],
        "economic_performance_metric_count": readiness[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": readiness["metric_computation_enabled"],
        "metric_computation_scope": readiness["metric_computation_scope"],
        "backtest_execution_enabled": readiness["backtest_execution_enabled"],
        "label_used_by_runtime_count": readiness["label_used_by_runtime_count"],
        "mapping_rule_modified_after_comparison_count": readiness[
            "mapping_rule_modified_after_comparison_count"
        ],
        "threshold_modified_after_metric_count": readiness[
            "threshold_modified_after_metric_count"
        ],
        "numeric_weight_added_count": readiness["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": readiness[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": readiness["role_count_voting_added_count"],
        "historical_tuning_leakage_count": readiness[
            "historical_tuning_leakage_count"
        ],
        "candidate_phase_emitted": readiness["candidate_phase_emitted"],
        "current_phase_emitted": readiness["current_phase_emitted"],
        "prohibited_metric_field_count": readiness[
            "prohibited_metric_field_count"
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
        "forbidden_repo_output_count": readiness["forbidden_repo_output_count"],
        "alpha25_freeze_hash_valid": freeze["alpha25_freeze_hash_valid"],
        "alpha24_parent_preserved": freeze["alpha24_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "historical_accuracy_metrics_computed_research_only_no_performance"
        ),
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 30,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase29_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase29_computes_research_only_accuracy_metrics_without_performance"
        ),
        "readiness": readiness,
        "freeze": freeze,
        "phase28_closure": phase28,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["readiness"]["historical_accuracy_metric_readiness_ready"]
        is True
        and summary["freeze"]["historical_accuracy_metrics_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase28_closure"]["result"] == "passed"
        and summary["phase28_closure"]["historical_accuracy_metric_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase29_historical_accuracy_metrics_closure"
    ]["expected"]
