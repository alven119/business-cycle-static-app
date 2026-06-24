from __future__ import annotations

from business_cycle.audits.historical_research_decision_outputs import (
    summarize_historical_research_decision_output_registry,
)


def test_historical_research_decision_output_registry_passes() -> None:
    summary = summarize_historical_research_decision_output_registry()

    assert summary["research_decision_output_registry_ready"] is True
    assert summary["research_decision_output_artifact_contract_ready"] is True
    assert summary["research_decision_output_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["research_decision_output_count"] == 5
    assert summary["output_mode_research_only_count"] == 5
    assert summary["predicted_label_output_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "none"
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
