from __future__ import annotations

from business_cycle.audits.historical_label_comparison_artifacts import (
    summarize_historical_label_comparison_artifacts,
)


def test_historical_label_comparison_artifact_registry_passes() -> None:
    summary = summarize_historical_label_comparison_artifacts()

    assert summary["label_comparison_artifact_registry_ready"] is True
    assert summary["label_comparison_artifact_contract_ready"] is True
    assert summary["label_comparison_artifact_generator_ready"] is True
    assert summary["label_joiner_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_provenance_verified_count"] == 5
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["label_comparison_executed"] is True
    assert summary["metric_computation_enabled"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["committed_artifacts_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
