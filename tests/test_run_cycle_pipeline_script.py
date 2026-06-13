from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


def test_run_cycle_pipeline_script_executes_without_pythonpath(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_dir = tmp_path / "derived"
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("FRED_API_KEY", None)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_cycle_pipeline.py",
            "--previous-phase-id",
            "recovery",
            "--indicator-id",
            "unemployment_rate",
            "--phase-id",
            "recovery",
            "--output-dir",
            str(output_dir),
        ],
        cwd=project_root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    snapshot_path = output_dir / "cycle_snapshot.json"
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_indicators"] == 1
    assert payload["summary"]["total_phases"] == 1
    assert not contains_key(payload, "investment_advice")
