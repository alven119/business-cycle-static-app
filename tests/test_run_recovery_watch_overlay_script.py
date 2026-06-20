from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.test_recovery_watch_overlay import write_spec


def test_run_recovery_watch_overlay_script_succeeds(tmp_path: Path) -> None:
    spec = write_spec(tmp_path)
    output = tmp_path / "overlay.json"

    completed = run_script("--spec", str(spec), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "global_recovery_watch_density_ratio=" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["scenario_count"] == 2
    assert "acceptance_summary" in payload


def test_run_recovery_watch_overlay_custom_spec_can_be_used(tmp_path: Path) -> None:
    spec = write_spec(tmp_path, scenario_ids=["global_financial_crisis"])
    output = tmp_path / "overlay.json"

    completed = run_script("--spec", str(spec), "--output", str(output), "--experiment-id", "custom")

    assert completed.returncode == 0, completed.stderr
    assert "experiment_id=custom" in completed.stdout


def test_run_recovery_watch_overlay_missing_spec_fails(tmp_path: Path) -> None:
    completed = run_script("--spec", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "recovery watch overlay spec does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_recovery_watch_overlay.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
