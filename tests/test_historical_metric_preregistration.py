from __future__ import annotations

from business_cycle.validation.historical_metric_preregistration import (
    load_historical_metric_registry,
    summarize_historical_metric_preregistration,
    summarize_historical_metric_registry,
)


def test_historical_metric_registry_preregisters_disabled_metrics() -> None:
    summary = summarize_historical_metric_registry()

    assert summary["historical_metric_registry_ready"] is True
    assert summary["preregistered_metric_count"] > 0
    assert summary["computation_enabled_metric_count"] == 0
    assert summary["metric_without_denominator_count"] == 0
    assert summary["metric_without_abstention_policy_count"] == 0
    assert summary["metric_without_blocked_policy_count"] == 0
    assert summary["metric_without_missing_policy_count"] == 0
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0


def test_historical_metric_preregistration_is_no_computation() -> None:
    summary = summarize_historical_metric_preregistration()

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
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0


def test_each_preregistered_metric_keeps_computation_disabled() -> None:
    registry = load_historical_metric_registry()

    for metric in registry["metrics"]:
        assert metric["computation_enabled"] is False
        assert metric["denominator_definition"]
        assert metric["numerator_definition"]
        assert metric["abstention_treatment"]
        assert metric["blocked_treatment"]
        assert metric["missing_treatment"]
        assert metric["prohibited_uses"]
