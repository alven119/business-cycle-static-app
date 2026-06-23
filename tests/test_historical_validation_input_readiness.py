from __future__ import annotations

from typing import Any

from business_cycle.validation.historical_validation_input_readiness import (
    build_scenario_input_readiness_outputs,
    load_historical_validation_input_readiness_contract,
    summarize_historical_validation_input_readiness,
)


def test_historical_validation_input_readiness_is_audit_only() -> None:
    summary = summarize_historical_validation_input_readiness()

    assert summary["historical_validation_input_readiness_contract_ready"] is True
    assert summary["scenario_input_requirements_ready"] is True
    assert summary["input_readiness_registry_ready"] is True
    assert summary["point_in_time_input_availability_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_id_mismatch_count"] == 0
    assert summary["scenario_with_complete_input_contract_count"] == 5
    assert summary["label_provenance_complete"] is True
    assert summary["missing_required_field_count"] == 0
    assert summary["forbidden_output_field_count"] == 0
    assert summary["model_execution_count"] == 0
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


def test_scenario_readiness_outputs_are_allowed_fields_only() -> None:
    contract = load_historical_validation_input_readiness_contract()
    outputs = build_scenario_input_readiness_outputs()

    assert len(outputs) == 5
    for output in outputs:
        assert set(output) == set(contract["allowed_outputs"])
        assert set(contract["forbidden_outputs"]).isdisjoint(_all_keys(output))
        assert output["readiness_label"] == "input_metadata_ready_validation_disabled"
        assert output["trust_metadata"]["model_executed"] is False
        assert output["trust_metadata"]["metrics_computed"] is False


def test_contract_disables_model_metric_and_network_paths() -> None:
    contract = load_historical_validation_input_readiness_contract()

    assert contract["no_network_policy_for_tests"]["network_allowed_in_tests"] is False
    assert contract["no_network_policy_for_tests"]["fred_api_allowed_in_tests"] is False
    assert contract["no_model_execution_policy"][
        "formal_decision_runtime_execution_allowed"
    ] is False
    assert contract["no_model_execution_policy"][
        "validation_harness_execution_allowed"
    ] is False
    assert contract["no_metric_computation_policy"][
        "metric_computation_enabled"
    ] is False
    assert contract["output_restrictions"]["candidate_phase_emitted"] is False
    assert contract["output_restrictions"]["current_phase_emitted"] is False


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()
