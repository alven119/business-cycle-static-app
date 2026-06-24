from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
    load_scenario_validation_trace_contract,
    summarize_scenario_validation_trace,
    validate_scenario_validation_trace,
    validate_scenario_validation_trace_contract,
    write_scenario_validation_trace,
)


FORBIDDEN_TRACE_FIELDS = {
    "accuracy",
    "precision",
    "recall",
    "f1",
    "hit_rate",
    "confusion_matrix",
    "economic_return",
    "excess_return",
    "sharpe",
    "max_drawdown",
    "CAGR",
    "trade_action",
    "portfolio_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "candidate_phase",
    "current_phase",
    "production_phase",
}


def test_scenario_validation_trace_contract_and_runtime_are_ready() -> None:
    summary = summarize_scenario_validation_trace()

    assert summary["scenario_validation_trace_contract_ready"] is True
    assert summary["scenario_validation_trace_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_trace_count"] == 5
    assert summary["prohibited_trace_field_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "diagnostic_summary_only"
    assert summary["backtest_execution_enabled"] is False


def test_scenario_validation_trace_schema_preserves_blockers() -> None:
    contract = load_scenario_validation_trace_contract()
    contract_validation = validate_scenario_validation_trace_contract(contract)
    run = build_scenario_validation_trace()

    assert contract_validation["contract_schema_valid"] is True
    assert len(run["scenario_validation_traces"]) == 5
    for trace in run["scenario_validation_traces"]:
        validation = validate_scenario_validation_trace(trace, contract=contract)
        assert validation["trace_schema_valid"] is True
        assert FORBIDDEN_TRACE_FIELDS.isdisjoint(_all_keys(trace))
        assert trace["comparison_status"] == "blocked"
        assert trace["comparable"] is False
        assert trace["blocked_reason_codes"]
        assert trace["label_runtime_usage_detected"] is False
        assert trace["candidate_phase_emitted"] is False
        assert trace["current_phase_emitted"] is False


def test_scenario_validation_trace_writer_uses_tmp_only(tmp_path: Path) -> None:
    run = build_scenario_validation_trace()
    output = tmp_path / "phase30_scenario_validation_trace.json"

    write_result = write_scenario_validation_trace(run, output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["scenario_validation_trace_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["scenario_count"] == 5
    assert payload["scenario_trace_count"] == 5
    assert payload["new_accuracy_metric_computed_count"] == 0
    assert payload["economic_performance_metric_count"] == 0
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False


def test_scenario_validation_trace_writer_rejects_repo_outputs() -> None:
    run = build_scenario_validation_trace()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_scenario_validation_trace(
            run,
            output="data/backtests/phase30_scenario_validation_trace.json",
        )


def test_generate_scenario_validation_trace_script(tmp_path: Path) -> None:
    output = tmp_path / "trace.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_scenario_validation_trace.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "scenario_validation_trace_contract_ready=true" in result.stdout
    assert "scenario_validation_trace_runtime_ready=true" in result.stdout
    assert "scenario_trace_count=5" in result.stdout
    assert "new_accuracy_metric_computed_count=0" in result.stdout
    assert output.is_file()


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()
