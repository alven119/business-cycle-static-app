from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from business_cycle.validation.validation_artifact_contracts import (
    load_validation_harness_contract,
)


def test_run_validation_harness_dry_run_script(tmp_path: Path) -> None:
    output_path = tmp_path / "validation_harness.json"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_validation_harness_dry_run.py",
            "--fixture-mode",
            "synthetic",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    contract = load_validation_harness_contract()
    assert "validation_harness_runtime_ready=true" in completed.stdout
    assert "synthetic_dry_run_executed=true" in completed.stdout
    assert "real_historical_validation_executed=false" in completed.stdout
    assert "metric_computation_enabled=false" in completed.stdout
    assert "candidate_phase_emitted=false" in completed.stdout
    assert set(payload) == set(contract["allowed_outputs"])
    assert set(contract["forbidden_outputs"]).isdisjoint(_all_keys(payload))


def test_run_validation_harness_dry_run_rejects_prohibited_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_validation_harness_dry_run.py",
            "--fixture-mode",
            "synthetic",
            "--output",
            "data/backtests/forbidden.json",
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
