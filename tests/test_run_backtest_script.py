from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_run_backtest_script_runs_one_period(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenario_id=global_financial_crisis" in completed.stdout
    assert "period_count=1" in completed.stdout
    assert (output_dir / "global_financial_crisis" / "timeline.json").exists()


def test_run_backtest_script_dry_run_does_not_write_output(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "2",
        "--output-dir",
        str(output_dir),
        "--dry-run",
    )

    assert completed.returncode == 0, completed.stderr
    assert "dry_run scenario_id=global_financial_crisis period_count=2" in completed.stdout
    assert not output_dir.exists()


def test_run_backtest_script_requires_scenario_id() -> None:
    completed = run_script()

    assert completed.returncode != 0
    assert "required" in completed.stderr


def test_run_backtest_script_unknown_scenario_fails() -> None:
    completed = run_script("--scenario-id", "missing")

    assert completed.returncode != 0
    assert "Unknown scenario_id: missing" in completed.stderr


def test_run_backtest_script_accepts_transition_controls(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
        "--transition-controls",
        "specs/backtests/transition_controls_experiment.yaml",
    )

    assert completed.returncode == 0, completed.stderr
    assert "period_count=1" in completed.stdout


def test_run_backtest_script_missing_transition_controls_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--transition-controls",
        str(tmp_path / "missing_controls.yaml"),
    )

    assert completed.returncode != 0
    assert "transition controls config does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_backtest.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
