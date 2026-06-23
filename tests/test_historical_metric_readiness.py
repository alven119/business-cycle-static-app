from __future__ import annotations

from business_cycle.audits.historical_metric_readiness import (
    summarize_historical_metric_readiness,
)


def test_historical_metric_readiness_passes_without_computation() -> None:
    summary = summarize_historical_metric_readiness()

    assert summary["metric_readiness_ready"] is True
    assert summary["historical_label_comparison_contract_ready"] is True
    assert summary["historical_metric_preregistration_ready"] is True
    assert summary["historical_metric_registry_ready"] is True
    assert summary["preregistered_metric_count"] > 0
    assert summary["label_runtime_usage_prohibited"] is True
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
