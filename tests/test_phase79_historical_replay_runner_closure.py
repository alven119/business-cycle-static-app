from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase79_historical_replay_runner_closure import (
    summarize_phase79_historical_replay_runner_closure,
)


def test_phase79_historical_replay_runner_closure_passes() -> None:
    summary = summarize_phase79_historical_replay_runner_closure()

    assert summary["result"] == "passed"
    assert summary["phase79_closure_ready"] is True
    assert summary["historical_replay_runner_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["replay_row_count"] == 10
    assert summary["strict_point_in_time_replay_row_count"] == 5
    assert summary["revised_diagnostic_replay_row_count"] == 5
    assert summary["data_mode_separation_valid"] is True
    assert summary["revised_mislabeled_as_point_in_time_count"] == 0
    assert summary["point_in_time_result_emitted_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["model_execution_count"] == 0
    assert summary["historical_validation_executed"] is False
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["generated_output_under_tmp_only"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase79_closure_status"]
        == "closed_historical_replay_runner_ready_strict_revised_separated_no_execution"
    )


def test_show_phase79_historical_replay_runner_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase79_historical_replay_runner_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase79_closure_ready=true" in completed.stdout
    assert "historical_replay_runner_ready=true" in completed.stdout
    assert "replay_row_count=10" in completed.stdout
    assert "result=passed" in completed.stdout
