"""Phase 23 comparison-coverage metrics registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_comparison_coverage_metrics import (
    summarize_historical_comparison_coverage_metrics,
)


DEFAULT_COMPARISON_COVERAGE_METRICS_REGISTRY_PATH = Path(
    "specs/audits/historical_comparison_coverage_metrics_registry.yaml"
)


def load_historical_comparison_coverage_metrics_registry(
    path: str | Path = DEFAULT_COMPARISON_COVERAGE_METRICS_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical comparison coverage metrics registry must map")
    registry = payload.get("historical_comparison_coverage_metrics_registry")
    if not isinstance(registry, dict):
        raise ValueError(
            "historical_comparison_coverage_metrics_registry must be a mapping"
        )
    return registry


def summarize_historical_comparison_coverage_metrics_registry(
    path: str | Path = DEFAULT_COMPARISON_COVERAGE_METRICS_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_historical_comparison_coverage_metrics_registry(path)
    metrics = summarize_historical_comparison_coverage_metrics()
    expected = registry["expected_counters"]
    storage = registry["metric_storage_policy"]
    ready = (
        registry["registry_status"]
        == "coverage_metrics_only_no_accuracy_or_performance"
        and metrics["comparison_coverage_metrics_contract_ready"] is True
        and metrics["comparison_coverage_metrics_runtime_ready"] is True
        and metrics["scenario_count"] == expected["scenario_count"]
        and metrics["label_comparison_artifact_count"]
        == expected["label_comparison_artifact_count"]
        and metrics["label_provenance_verified_count"]
        == expected["label_provenance_verified_count"]
        and metrics["label_used_by_runtime_count"]
        == expected["label_used_by_runtime_count"]
        and metrics["comparison_coverage_metric_count"]
        == expected["comparison_coverage_metric_count"]
        and metrics["metric_computation_enabled"]
        is expected["metric_computation_enabled"]
        and metrics["metric_computation_scope"]
        == expected["metric_computation_scope"]
        and metrics["historical_accuracy_metric_count"]
        == expected["historical_accuracy_metric_count"]
        and metrics["economic_performance_metric_count"]
        == expected["economic_performance_metric_count"]
        and metrics["prohibited_metric_field_count"]
        == expected["prohibited_metric_field_count"]
        and metrics["predicted_label_output_count"]
        == expected["predicted_label_output_count"]
        and metrics["candidate_phase_emitted"]
        is expected["candidate_phase_emitted"]
        and metrics["current_phase_emitted"] is expected["current_phase_emitted"]
        and storage["committed_artifacts_allowed"] is False
        and storage["tmp_artifacts_allowed"] is True
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
    )
    return {
        "phase": "23",
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "comparison_coverage_metrics_registry_ready": ready,
        "comparison_coverage_metrics_contract_ready": metrics[
            "comparison_coverage_metrics_contract_ready"
        ],
        "comparison_coverage_metrics_runtime_ready": metrics[
            "comparison_coverage_metrics_runtime_ready"
        ],
        "scenario_count": metrics["scenario_count"],
        "label_comparison_artifact_count": metrics[
            "label_comparison_artifact_count"
        ],
        "label_provenance_verified_count": metrics[
            "label_provenance_verified_count"
        ],
        "label_used_by_runtime_count": metrics["label_used_by_runtime_count"],
        "comparison_coverage_metric_count": metrics[
            "comparison_coverage_metric_count"
        ],
        "metric_computation_enabled": metrics["metric_computation_enabled"],
        "metric_computation_scope": metrics["metric_computation_scope"],
        "historical_accuracy_metric_count": metrics[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": metrics[
            "economic_performance_metric_count"
        ],
        "prohibited_metric_field_count": metrics["prohibited_metric_field_count"],
        "predicted_label_output_count": metrics["predicted_label_output_count"],
        "candidate_phase_emitted": metrics["candidate_phase_emitted"],
        "current_phase_emitted": metrics["current_phase_emitted"],
        "backtest_execution_enabled": metrics["backtest_execution_enabled"],
        "holdout_registered": metrics["holdout_registered"],
        "production_behavior_change_count": metrics[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": metrics[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": metrics[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": metrics["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": metrics[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": metrics["role_count_voting_added_count"],
        "historical_tuning_leakage_count": metrics[
            "historical_tuning_leakage_count"
        ],
        "committed_artifacts_allowed": storage["committed_artifacts_allowed"],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage["data_prospective_write_allowed"],
        "public_output_allowed": storage["public_output_allowed"],
        "coverage_metrics": metrics["coverage_metrics"],
        "registry": registry,
        "metrics": metrics,
    }
