from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_calibration_plan_script_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "diagnosed_issue_count=5" in completed.stdout
    assert "candidate_controls=" in completed.stdout
    assert "confirmation_period" in completed.stdout
    assert "in_sample_scenarios=dotcom_bubble,global_financial_crisis,covid_recession" in completed.stdout
    assert "out_of_sample_scenarios=euro_debt_slowdown,late_cycle_2018" in completed.stdout
    assert "acceptance_criteria_count=5" in completed.stdout
    assert "next_phases=7B:" in completed.stdout


def test_show_calibration_plan_script_accepts_custom_plan(tmp_path: Path) -> None:
    source = Path("specs/backtests/calibration_plan.yaml")
    custom = tmp_path / "calibration_plan.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--plan", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout


def test_show_calibration_plan_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--plan", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Calibration plan file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_calibration_plan.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
