from __future__ import annotations

from business_cycle.audits.historical_validation_readiness import (
    summarize_historical_validation_readiness,
)


def test_historical_validation_readiness_keeps_execution_disabled() -> None:
    summary = summarize_historical_validation_readiness()

    assert summary["historical_validation_readiness_ready"] is True
    assert summary["historical_validation_manifest_contract_ready"] is True
    assert summary["historical_validation_scenario_manifest_ready"] is True
    assert summary["validation_label_policy_ready"] is True
    assert summary["scenario_count"] > 0
    assert summary["point_in_time_requirement_present"] is True
    assert summary["label_provenance_complete"] is True
    assert summary["label_runtime_usage_prohibited"] is True
    assert summary["no_tuning_after_manifest_rule_present"] is True
    assert summary["real_historical_validation_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
