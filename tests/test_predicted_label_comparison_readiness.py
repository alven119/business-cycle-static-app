from __future__ import annotations

from business_cycle.audits.predicted_label_comparison_readiness import (
    summarize_predicted_label_comparison_readiness,
)


def test_predicted_label_comparison_readiness_is_ready() -> None:
    summary = summarize_predicted_label_comparison_readiness()

    assert summary["predicted_label_comparison_artifact_contract_ready"] is True
    assert summary["predicted_label_comparison_generator_ready"] is True
    assert summary["predicted_label_comparison_readiness_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["predicted_label_artifact_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_comparison_executed"] is True
    assert summary["predicted_label_provenance_verified_count"] == 5
    assert summary["historical_label_provenance_verified_count"] == 5
    assert summary["mapping_contract_hash_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["tmp_comparison_artifacts_allowed"] is True
    assert summary["committed_comparison_artifacts_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
