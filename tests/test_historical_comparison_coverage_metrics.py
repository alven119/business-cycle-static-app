from __future__ import annotations

from business_cycle.validation.historical_comparison_coverage_metrics import (
    summarize_historical_comparison_coverage_metrics,
    validate_historical_comparison_coverage_metrics,
)


def test_comparison_coverage_metrics_are_scope_limited() -> None:
    summary = summarize_historical_comparison_coverage_metrics()

    assert summary["comparison_coverage_metrics_contract_ready"] is True
    assert summary["comparison_coverage_metrics_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_provenance_verified_count"] == 5
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["comparison_coverage_metric_count"] > 0
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "comparison_coverage_only"
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["prohibited_metric_field_count"] == 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_coverage_metric_values_are_structural_counts_and_rates() -> None:
    summary = summarize_historical_comparison_coverage_metrics()
    metrics = summary["coverage_metrics"]

    assert metrics["label_join_success_count"] == 5
    assert metrics["label_join_coverage_rate"] == 1.0
    assert metrics["label_provenance_verified_count"] == 5
    assert metrics["label_provenance_coverage_rate"] == 1.0
    assert metrics["runtime_result_available_count"] == 5
    assert metrics["runtime_result_availability_rate"] == 1.0
    assert metrics["comparable_artifact_count"] == 5
    assert metrics["non_comparable_artifact_count"] == 0
    assert metrics["accuracy_metric_enabled"] is False
    assert metrics["economic_performance_metric_enabled"] is False


def test_forbidden_prediction_or_accuracy_fields_are_rejected() -> None:
    summary = summarize_historical_comparison_coverage_metrics()
    metrics = dict(summary["coverage_metrics"])
    metrics["predicted_label"] = "recession"

    validation = validate_historical_comparison_coverage_metrics(metrics)

    assert validation["metric_schema_valid"] is False
    assert validation["predicted_label_output_count"] == 1
    assert validation["prohibited_metric_field_count"] == 1
