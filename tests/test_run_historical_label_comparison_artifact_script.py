from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from business_cycle.validation.historical_label_comparison_artifacts import (
    load_historical_label_comparison_artifact_contract,
)


def test_run_historical_label_comparison_artifact_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "phase22_label_comparison"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_label_comparison_artifact.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    contract = load_historical_label_comparison_artifact_contract()
    artifact_paths = sorted(path for path in output_dir.glob("*.json"))
    scenario_artifacts = [
        path
        for path in artifact_paths
        if path.name != "label_comparison_summary.json"
    ]
    assert "label_comparison_artifact_contract_ready=true" in stdout
    assert "label_comparison_artifact_count=5" in stdout
    assert "label_comparison_executed=true" in stdout
    assert "metric_computation_enabled=false" in stdout
    assert "historical_accuracy_metric_count=0" in stdout
    assert "candidate_phase_emitted=false" in stdout
    assert len(scenario_artifacts) == 5
    forbidden = set(contract["forbidden_artifact_fields"])
    for artifact_path in scenario_artifacts:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert payload["label_used_by_runtime"] is False
        assert payload["metric_computation_enabled"] is False
        assert forbidden.isdisjoint(_all_keys(payload))


def test_run_historical_label_comparison_artifact_rejects_repo_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_label_comparison_artifact.py",
            "--output-dir",
            "data/backtests/phase22",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "under /tmp" in completed.stderr


def test_label_comparison_script_does_not_write_forbidden_repo_outputs(
    tmp_path: Path,
) -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_label_comparison_artifact.py",
            "--output-dir",
            str(tmp_path / "phase22_label_comparison"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    for root in ("data/backtests", "data/prospective", "public"):
        path = Path(root)
        assert not path.exists() or not any(item.is_file() for item in path.rglob("*"))


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
