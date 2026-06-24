from __future__ import annotations

from business_cycle.validation.offline_predicted_label_mapping_contract import (
    load_offline_predicted_label_mapping_contract,
    summarize_offline_predicted_label_mapping_contract,
    validate_offline_predicted_label_mapping_contract,
)


def test_offline_predicted_label_mapping_contract_is_preregistered_only() -> None:
    summary = summarize_offline_predicted_label_mapping_contract()

    assert summary["predicted_label_mapping_contract_ready"] is True
    assert summary["research_decision_state_taxonomy_ready"] is True
    assert summary["offline_predicted_label_taxonomy_ready"] is True
    assert summary["mapping_rule_count"] > 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["predicted_label_artifact_count"] == 0
    assert summary["label_comparison_executed"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0


def test_mapping_contract_distinguishes_output_layers() -> None:
    contract = load_offline_predicted_label_mapping_contract()
    validation = validate_offline_predicted_label_mapping_contract(contract)

    assert validation["contract_schema_valid"] is True
    assert "research_decision_output.decision_state" in contract["allowed_inputs"]
    assert "expected_label" in contract["prohibited_inputs"]
    assert "candidate_phase" in contract["prohibited_inputs"]
    assert "current_phase" in contract["prohibited_inputs"]
    assert "production_phase" in contract["prohibited_inputs"]
    assert contract["label_usage_policy"]["labels_may_be_used_by_runtime"] is False
    assert (
        contract["candidate_phase_prohibition"]["candidate_phase_output_allowed"]
        is False
    )
    assert contract["current_phase_prohibition"]["current_phase_output_allowed"] is False
    assert (
        contract["production_phase_prohibition"]["production_phase_output_allowed"]
        is False
    )
    assert all(
        rule["emission_allowed_this_phase"] is False
        for rule in contract["mapping_rules"]
    )


def test_mapping_contract_rejects_emitting_mapping_rule() -> None:
    contract = load_offline_predicted_label_mapping_contract()
    contract["mapping_rules"] = [dict(rule) for rule in contract["mapping_rules"]]
    contract["mapping_rules"][0]["emission_allowed_this_phase"] = True

    validation = validate_offline_predicted_label_mapping_contract(contract)

    assert validation["contract_schema_valid"] is False
    assert validation["mapping_rules_non_emitting"] is False
