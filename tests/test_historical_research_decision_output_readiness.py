from __future__ import annotations

from business_cycle.audits.historical_research_decision_output_readiness import (
    summarize_historical_research_decision_output_readiness,
)


def test_historical_research_decision_output_readiness_passes() -> None:
    summary = summarize_historical_research_decision_output_readiness()

    assert summary["research_decision_output_contract_ready"] is True
    assert summary["research_decision_output_readiness_ready"] is True
    assert summary["output_taxonomy_ready"] is True
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
    assert summary["committed_decision_outputs_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
