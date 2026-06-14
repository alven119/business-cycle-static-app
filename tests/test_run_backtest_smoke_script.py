from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_backtest_smoke_script_runs_one_period(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    output_path = tmp_path / "smoke_summary.json"

    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenario_count=1" in completed.stdout
    assert "max_periods=1" in completed.stdout
    assert output_path.exists()


def test_run_backtest_smoke_script_scenario_id_runs_single_scenario(tmp_path: Path) -> None:
    output_path = tmp_path / "smoke_summary.json"

    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert completed.returncode == 0, completed.stderr
    assert payload["scenario_count"] == 1
    assert payload["scenarios"][0]["scenario_id"] == "global_financial_crisis"


def test_run_backtest_smoke_script_output_can_be_customized(tmp_path: Path) -> None:
    output_path = tmp_path / "custom" / "summary.json"

    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["output_path"] == str(output_path)


def test_run_backtest_smoke_script_unknown_scenario_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--scenario-id",
        "missing",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--output",
        str(tmp_path / "summary.json"),
    )

    assert completed.returncode != 0
    assert "Unknown scenario_id: missing" in completed.stderr


def test_run_backtest_smoke_script_accepts_transition_controls(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    output_path = tmp_path / "smoke_summary.json"

    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
        "--output",
        str(output_path),
        "--transition-controls",
        "specs/backtests/transition_controls_experiment.yaml",
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenario_count=1" in completed.stdout
    assert output_path.exists()


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_backtest_smoke.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
