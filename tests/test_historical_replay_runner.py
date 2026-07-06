from __future__ import annotations

import json
import subprocess
import sys

import pytest

from business_cycle.validation.historical_replay_runner import (
    HistoricalReplayRunnerContractError,
    build_historical_replay_runner_preview,
    load_historical_replay_runner_contract,
    summarize_historical_replay_runner_preview,
    write_historical_replay_runner_preview,
)


def test_phase79_historical_replay_runner_passes() -> None:
    summary = summarize_historical_replay_runner_preview()

    assert summary["result"] == "passed"
    assert summary["historical_replay_runner_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["replay_data_mode_count"] == 2
    assert summary["replay_row_count"] == 10
    assert summary["strict_point_in_time_replay_row_count"] == 5
    assert summary["revised_diagnostic_replay_row_count"] == 5
    assert summary["scenario_with_replay_rows_count"] == 5
    assert summary["transition_timing_replay_preview_ready"] is True
    assert summary["policy_replay_schedule_contract_ready"] is True
    assert summary["cash_flow_kernel_contract_ready"] is True
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
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase79_replay_rows_preserve_strict_revised_separation() -> None:
    artifact = build_historical_replay_runner_preview()
    rows = artifact["replay_rows"]
    strict_rows = [row for row in rows if row["data_mode"] == "vintage_as_of"]
    revised_rows = [
        row for row in rows if row["data_mode"] == "revised_declared_comparison_only"
    ]

    assert len(strict_rows) == len(revised_rows) == 5
    assert all(row["revised_diagnostic_label"] is None for row in strict_rows)
    assert all(
        row["revised_diagnostic_label"] == "revised_diagnostic_only"
        for row in revised_rows
    )
    assert all(row["point_in_time_result_emitted"] is False for row in rows)
    assert all(row["label_used_by_runtime"] is False for row in rows)
    assert all(row["model_executed"] is False for row in rows)
    assert artifact["prohibited_replay_output_field_count"] == 0


def test_phase79_contract_disables_execution_paths() -> None:
    contract = load_historical_replay_runner_contract()

    assert contract["output_policy"]["output_mode"] == "historical_replay_runner_preview_only"
    assert contract["output_policy"]["replay_execution_allowed_now"] is False
    assert contract["output_policy"]["formal_decision_runtime_execution_allowed"] is False
    assert contract["output_policy"]["validation_execution_allowed"] is False
    assert contract["output_policy"]["label_comparison_allowed"] is False
    assert contract["output_policy"]["metric_computation_allowed"] is False
    assert contract["output_policy"]["backtest_execution_allowed"] is False
    assert contract["output_policy"]["generated_output_under_tmp_only"] is True
    assert all(value is False for value in contract["disabled_runtime_guards"].values())


def test_phase79_preview_writer_requires_tmp_output(tmp_path) -> None:
    output = tmp_path / "phase79_replay_preview.json"

    artifact = write_historical_replay_runner_preview(output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert artifact["historical_replay_runner_ready"] is True
    assert payload["historical_replay_runner_ready"] is True
    assert len(payload["replay_rows"]) == 10

    with pytest.raises(HistoricalReplayRunnerContractError):
        write_historical_replay_runner_preview("phase79_replay_preview.json")


def test_show_historical_replay_runner_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_historical_replay_runner.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_replay_runner_ready=true" in completed.stdout
    assert "replay_row_count=10" in completed.stdout
    assert "revised_mislabeled_as_point_in_time_count=0" in completed.stdout
    assert "result=passed" in completed.stdout


def test_run_historical_replay_runner_preview_script(tmp_path) -> None:
    output = tmp_path / "phase79_replay_preview.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_replay_runner_preview.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_replay_runner_ready=true" in completed.stdout
    assert "replay_row_count=10" in completed.stdout
    assert output.exists()
