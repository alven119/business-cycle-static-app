from __future__ import annotations

from business_cycle.validation.historical_label_comparison_contract import (
    load_historical_label_comparison_contract,
    summarize_historical_label_comparison_contract,
)


def test_historical_label_comparison_contract_is_preregistered_only() -> None:
    summary = summarize_historical_label_comparison_contract()

    assert summary["historical_label_comparison_contract_ready"] is True
    assert summary["label_runtime_usage_prohibited"] is True
    assert summary["required_dry_run_result_count"] == 5
    assert summary["dry_run_result_registry_ready"] is True
    assert summary["dry_run_result_count"] == 5
    assert summary["label_join_policy_ready"] is True
    assert summary["denominator_policy_ready"] is True
    assert summary["abstention_handling_policy_ready"] is True
    assert summary["blocked_result_handling_policy_ready"] is True
    assert summary["missing_result_handling_policy_ready"] is True
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0


def test_historical_label_comparison_contract_forbids_runtime_label_use() -> None:
    contract = load_historical_label_comparison_contract()

    assert contract["label_source_policy"]["label_runtime_usage_prohibited"] is True
    assert contract["expected_label_output_policy"][
        "expected_label_materialization_allowed_this_phase"
    ] is False
    assert contract["expected_label_output_policy"][
        "expected_label_allowed_in_runtime_input"
    ] is False
    assert contract["predicted_label_output_policy"][
        "predicted_label_materialization_allowed_this_phase"
    ] is False
    assert contract["predicted_label_output_policy"][
        "candidate_phase_must_not_be_used_as_prediction"
    ] is True
    assert contract["predicted_label_output_policy"][
        "current_phase_must_not_be_used_as_prediction"
    ] is True
