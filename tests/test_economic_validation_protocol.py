from __future__ import annotations

from business_cycle.validation.economic_validation_protocol import (
    load_economic_validation_protocol,
    summarize_economic_validation_protocol,
)


def test_economic_validation_protocol_is_preregistered_without_execution() -> None:
    summary = summarize_economic_validation_protocol()

    assert summary["economic_validation_protocol_ready"] is True
    assert summary["validation_layer_count"] >= 5
    assert summary["missing_required_field_count"] == 0
    assert summary["retrospective_diagnostic_distinguished_from_validation"] is True
    assert summary["historical_accuracy_validation_not_started"] is True
    assert summary["economic_validation_not_started"] is True
    assert summary["prospective_validation_not_started"] is True
    assert summary["holdout_registered"] is False
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["backtest_or_metric_execution_count"] == 0
    assert summary["validation_execution_started_count"] == 0


def test_economic_validation_protocol_declares_required_policies() -> None:
    protocol = load_economic_validation_protocol()

    for required in (
        "structural_validation",
        "retrospective_diagnostic",
        "historical_accuracy_validation",
        "economic_validation",
        "prospective_validation",
    ):
        assert required in {row["layer_id"] for row in protocol["validation_layers"]}
    assert protocol["retrospective_diagnostic_policy"][
        "distinguished_from_validation"
    ] is True
    assert protocol["historical_accuracy_validation_policy"][
        "metric_computation_enabled"
    ] is False
    assert protocol["prospective_validation_policy"][
        "prospective_registry_record_count"
    ] == 0
    assert protocol["holdout_registration_policy"]["holdout_registered"] is False
