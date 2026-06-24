from __future__ import annotations

from business_cycle.validation.historical_research_decision_output_contract import (
    load_historical_research_decision_output_contract,
    summarize_historical_research_decision_output_contract,
    validate_historical_research_decision_output_contract,
)


def test_historical_research_decision_output_contract_is_preregistered_only() -> None:
    summary = summarize_historical_research_decision_output_contract()

    assert summary["research_decision_output_contract_ready"] is True
    assert summary["output_taxonomy_ready"] is True
    assert summary["future_allowed_field_count"] == 13
    assert summary["forbidden_output_field_count"] == 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["research_decision_output_emitted"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["accuracy_metric_enabled"] is False
    assert summary["economic_performance_metric_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0


def test_future_schema_rejects_forbidden_decision_fields() -> None:
    contract = load_historical_research_decision_output_contract()
    contract["future_allowed_fields"] = [
        *contract["future_allowed_fields"],
        "candidate_phase",
        "historical_accuracy",
    ]

    validation = validate_historical_research_decision_output_contract(contract)

    assert validation["contract_schema_valid"] is False
    assert validation["future_forbidden_field_count"] == 2
    assert validation["forbidden_output_field_count"] == 2
    assert validation["future_forbidden_fields"] == [
        "candidate_phase",
        "historical_accuracy",
    ]
