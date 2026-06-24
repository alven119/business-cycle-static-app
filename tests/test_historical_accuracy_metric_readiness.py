from __future__ import annotations

from business_cycle.audits.historical_accuracy_metric_readiness import (
    summarize_historical_accuracy_metric_readiness,
)


def test_historical_accuracy_metric_readiness_is_ready() -> None:
    summary = summarize_historical_accuracy_metric_readiness()

    assert summary["historical_accuracy_metric_artifact_contract_ready"] is True
    assert summary["historical_accuracy_metric_runtime_ready"] is True
    assert summary["historical_accuracy_metric_readiness_ready"] is True
    assert summary["preregistered_metric_registry_used"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["comparable_scenario_count"] == 0
    assert summary["non_comparable_scenario_count"] == 0
    assert summary["abstained_scenario_count"] == 0
    assert summary["blocked_scenario_count"] == 5
    assert summary["taxonomy_mismatch_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "historical_accuracy_only"
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["mapping_rule_modified_after_comparison_count"] == 0
    assert summary["threshold_modified_after_metric_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_metric_field_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
