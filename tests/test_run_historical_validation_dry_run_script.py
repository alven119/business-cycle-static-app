from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from business_cycle.validation.historical_validation_result_writer import (
    load_historical_validation_dry_run_contract,
)


def test_run_historical_validation_dry_run_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "phase20_dry_run"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_validation_dry_run.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    contract = load_historical_validation_dry_run_contract()
    artifact_paths = sorted(path for path in output_dir.glob("*.json"))
    scenario_artifacts = [
        path for path in artifact_paths if path.name != "dry_run_summary.json"
    ]
    assert "historical_validation_dry_run_contract_ready=true" in stdout
    assert "historical_validation_dry_run_executed=true" in stdout
    assert "scenario_dry_run_result_count=5" in stdout
    assert "model_execution_count=5" in stdout
    assert "historical_accuracy_metric_count=0" in stdout
    assert "candidate_phase_emitted=false" in stdout
    assert len(scenario_artifacts) == 5
    forbidden = set(contract["forbidden_result_fields"])
    for artifact_path in scenario_artifacts:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert payload["label_used_by_runtime"] is False
        assert payload["decision_runtime_executed"] is True
        assert forbidden.isdisjoint(_all_keys(payload))


def test_run_historical_validation_dry_run_rejects_repo_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_validation_dry_run.py",
            "--output-dir",
            "data/backtests/phase20",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "under /tmp" in completed.stderr


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
