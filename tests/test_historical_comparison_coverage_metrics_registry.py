from __future__ import annotations

from business_cycle.audits.historical_comparison_coverage_metrics import (
    summarize_historical_comparison_coverage_metrics_registry,
)


def test_historical_comparison_coverage_metrics_registry_passes() -> None:
    summary = summarize_historical_comparison_coverage_metrics_registry()

    assert summary["comparison_coverage_metrics_registry_ready"] is True
    assert summary["comparison_coverage_metrics_contract_ready"] is True
    assert summary["comparison_coverage_metrics_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_provenance_verified_count"] == 5
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["comparison_coverage_metric_count"] == 14
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "comparison_coverage_only"
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["prohibited_metric_field_count"] == 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["committed_artifacts_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
