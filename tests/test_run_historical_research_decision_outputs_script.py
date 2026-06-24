from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


FORBIDDEN_FIELDS = {
    "predicted_label",
    "expected_label",
    "candidate_phase",
    "current_phase",
    "selected_phase",
    "winning_phase",
    "historical_accuracy",
    "confusion_matrix",
    "precision",
    "recall",
    "hit_rate",
    "economic_performance",
    "portfolio_return",
    "CAGR",
    "drawdown",
    "Sharpe",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
}


def test_run_historical_research_decision_outputs_writes_only_tmp_artifacts(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "phase25_outputs"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_research_decision_outputs.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = result.stdout
    assert "research_decision_output_artifact_contract_ready=true" in stdout
    assert "research_decision_output_runtime_ready=true" in stdout
    assert "research_decision_output_count=5" in stdout
    assert "predicted_label_output_count=0" in stdout
    assert "historical_accuracy_metric_count=0" in stdout
    assert "economic_performance_metric_count=0" in stdout

    payload = json.loads((output_dir / "research_decision_outputs.json").read_text())
    assert payload["research_decision_output_count"] == 5
    assert payload["metric_computation_scope"] == "none"
    assert payload["historical_accuracy_metric_count"] == 0
    assert payload["economic_performance_metric_count"] == 0
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False
    for artifact in payload["research_decision_outputs"]:
        assert artifact["output_mode"] == "research_historical_validation_only"
        assert artifact["label_used_by_runtime"] is False
        assert FORBIDDEN_FIELDS.isdisjoint(_all_keys(artifact))


def test_run_historical_research_decision_outputs_rejects_repo_output_path() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_research_decision_outputs.py",
            "--output-dir",
            "data/backtests/phase25_research_decision_outputs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "must be under /tmp" in result.stderr


def test_script_does_not_write_forbidden_repo_outputs(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_research_decision_outputs.py",
            "--output-dir",
            str(tmp_path / "phase25_outputs"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    forbidden_files: list[Path] = []
    for root in (Path("data/backtests"), Path("data/prospective"), Path("public")):
        if root.exists():
            forbidden_files.extend(item for item in root.rglob("*") if item.is_file())
    assert forbidden_files == []


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
