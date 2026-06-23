from __future__ import annotations

from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_manifest_contract,
    summarize_historical_validation_manifest,
)


def test_historical_validation_manifest_is_preregistered_only() -> None:
    summary = summarize_historical_validation_manifest()

    assert summary["historical_validation_manifest_contract_ready"] is True
    assert summary["historical_validation_scenario_manifest_ready"] is True
    assert summary["scenario_count"] > 0
    assert summary["scenario_id_mismatch_count"] == 0
    assert summary["window_definition_mismatch_count"] == 0
    assert summary["missing_required_field_count"] == 0
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
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["scenario_execution_started_count"] == 0
    assert summary["metric_or_backtest_count"] == 0
    assert summary["candidate_or_current_phase_read_count"] == 0
    assert summary["disabled_runtime_guards_hold"] is True


def test_manifest_contract_contains_required_phase17_policies() -> None:
    contract = load_historical_validation_manifest_contract()

    assert contract["manifest_status"] == "preregistered_no_validation_execution"
    assert contract["scenario_selection_policy"][
        "result_based_selection_allowed"
    ] is False
    assert contract["point_in_time_requirements"]["point_in_time_required"] is True
    assert contract["revised_data_allowed_only_for_declared_comparison"] is True
    assert contract["label_usage_restrictions"][
        "runtime_decision_logic_allowed"
    ] is False
    assert contract["label_usage_restrictions"][
        "rule_or_evaluator_tuning_allowed"
    ] is False
    assert contract["metric_preregistration_dependency"][
        "metric_computation_enabled"
    ] is False
    assert contract["output_restrictions"]["candidate_phase_emitted"] is False
    assert contract["output_restrictions"]["current_phase_emitted"] is False
