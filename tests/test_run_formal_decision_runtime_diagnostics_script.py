from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


FORBIDDEN_OUTPUTS = {
    "candidate_phase",
    "current_phase",
    "winning_phase",
    "selected_phase",
    "selected_candidate_phase",
    "phase_rank",
    "phase_score",
    "phase_probability",
    "confidence_score",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "allocation_recommendation",
    "backtest_performance",
    "accuracy_metric",
}


def test_run_formal_decision_runtime_diagnostics_script(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "decision_runtime.json"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_formal_decision_runtime_diagnostics.py",
            "--as-of",
            "2019-12-31",
            "--data-mode",
            "revised",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert "non_emitting_decision_runtime_ready=true" in stdout
    assert "evaluated_precondition_rule_count=10" in stdout
    assert "candidate_phase_emitted=false" in stdout
    assert payload["candidate_selection_enabled"] is False
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False
    assert FORBIDDEN_OUTPUTS.isdisjoint(_all_keys(payload))


def test_run_formal_decision_runtime_diagnostics_rejects_prohibited_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_formal_decision_runtime_diagnostics.py",
            "--as-of",
            "2019-12-31",
            "--data-mode",
            "revised",
            "--output",
            "data/prospective/forbidden.json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "refusing prohibited output path" in completed.stderr


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
