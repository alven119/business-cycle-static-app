from __future__ import annotations

from business_cycle.validation.historical_validation_execution_readiness import (
    load_historical_validation_execution_readiness_contract,
    summarize_historical_validation_execution_readiness,
)


def test_historical_validation_execution_readiness_gate_is_closed() -> None:
    summary = summarize_historical_validation_execution_readiness()

    assert summary["historical_validation_execution_readiness_contract_ready"] is True
    assert summary["historical_validation_execution_plan_ready"] is True
    assert summary["result_artifact_contract_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_with_execution_plan_count"] == 5
    assert summary["prior_freeze_dependency_complete"] is True
    assert summary["decision_runtime_dependency_complete"] is True
    assert summary["validation_protocol_dependency_complete"] is True
    assert summary["validation_harness_dependency_complete"] is True
    assert summary["input_readiness_dependency_complete"] is True
    assert summary["label_policy_dependency_complete"] is True
    assert summary["execution_allowed_in_this_phase"] is False
    assert summary["missing_required_field_count"] == 0
    assert summary["model_execution_count"] == 0
    assert summary["real_historical_validation_executed"] is False
    assert summary["historical_validation_result_count"] == 0
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
    assert summary["execution_readiness_gate_ready"] is True


def test_execution_readiness_contract_forbids_phase19_execution() -> None:
    contract = load_historical_validation_execution_readiness_contract()

    assert contract["no_execution_policy_for_this_phase"][
        "execution_allowed_in_this_phase"
    ] is False
    assert contract["no_execution_policy_for_this_phase"][
        "formal_decision_runtime_execution_allowed"
    ] is False
    assert contract["metric_computation_policy"]["metric_computation_enabled"] is False
    assert contract["backtest_execution_policy"]["backtest_execution_enabled"] is False
    assert contract["holdout_policy"]["holdout_registered"] is False
    assert contract["output_restrictions"]["candidate_phase_emitted"] is False
    assert contract["output_restrictions"]["current_phase_emitted"] is False
