from __future__ import annotations

from business_cycle.audits.validation_readiness import summarize_validation_readiness


def test_validation_readiness_registry_keeps_validation_disabled() -> None:
    summary = summarize_validation_readiness()

    assert summary["validation_readiness_registry_ready"] is True
    assert summary["validation_layer_count"] >= 5
    assert summary["layer_mismatch_count"] == 0
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
    assert summary["production_behavior_change_count"] == 0
