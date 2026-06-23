from __future__ import annotations

from business_cycle.audits.historical_validation_dry_run_results import (
    summarize_historical_validation_dry_run_results,
)


def test_historical_validation_dry_run_result_registry_passes() -> None:
    summary = summarize_historical_validation_dry_run_results()

    assert summary["historical_validation_dry_run_result_registry_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_dry_run_result_count"] == 5
    assert summary["model_execution_count"] == 5
    assert summary["real_historical_validation_executed"] is True
    assert summary["label_blind_execution_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["prohibited_result_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["committed_artifacts_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
