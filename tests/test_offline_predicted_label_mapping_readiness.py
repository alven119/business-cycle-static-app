from __future__ import annotations

from business_cycle.audits.offline_predicted_label_mapping_readiness import (
    summarize_offline_predicted_label_mapping_readiness,
)


def test_offline_predicted_label_mapping_readiness_passes() -> None:
    summary = summarize_offline_predicted_label_mapping_readiness()

    assert summary["predicted_label_mapping_contract_ready"] is True
    assert summary["predicted_label_mapping_readiness_ready"] is True
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
    assert summary["committed_predicted_label_artifacts_allowed"] is False
    assert summary["tmp_predicted_label_artifacts_allowed"] is False
    assert summary["data_backtests_write_allowed"] is False
    assert summary["data_prospective_write_allowed"] is False
    assert summary["public_output_allowed"] is False
