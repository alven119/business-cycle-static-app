from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase80_research_backtest_artifacts_closure import (
    summarize_phase80_research_backtest_artifacts_closure,
)


def test_phase80_research_backtest_artifacts_closure_passes() -> None:
    summary = summarize_phase80_research_backtest_artifacts_closure()

    assert summary["result"] == "passed"
    assert summary["phase80_closure_ready"] is True
    assert summary["research_backtest_artifact_contract_ready"] is True
    assert summary["research_backtest_artifact_generator_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["source_replay_row_count"] == 10
    assert summary["research_backtest_artifact_count"] == 10
    assert summary["metric_value_count"] == 0
    assert summary["risk_metric_value_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert (
        summary["phase80_closure_status"]
        == "closed_research_backtest_artifacts_generated_no_public_output_or_metrics"
    )


def test_show_phase80_research_backtest_artifacts_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase80_research_backtest_artifacts_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase80_closure_ready=true" in completed.stdout
    assert "research_backtest_artifact_generator_ready=true" in completed.stdout
    assert "research_backtest_artifact_count=10" in completed.stdout
    assert "metric_value_count=0" in completed.stdout
    assert "public_output_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
