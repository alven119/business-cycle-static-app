from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_list_backtest_scenarios_script_lists_all_scenarios() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "scenario_id=dotcom_bubble" in completed.stdout
    assert "scenario_id=global_financial_crisis" in completed.stdout
    assert "scenario_id=covid_recession" in completed.stdout
    assert "FRED_API_KEY" not in completed.stdout


def test_list_backtest_scenarios_script_lists_one_scenario() -> None:
    completed = run_script("--scenario-id", "dotcom_bubble")

    assert completed.returncode == 0, completed.stderr
    assert "scenario_id=dotcom_bubble" in completed.stdout
    assert "display_name_zh=網路泡沫" in completed.stdout
    assert "expected_focus_zh:" in completed.stdout
    assert "scenario_id=global_financial_crisis" not in completed.stdout


def test_list_backtest_scenarios_script_missing_scenario_fails() -> None:
    completed = run_script("--scenario-id", "missing")

    assert completed.returncode != 0
    assert "Unknown scenario_id: missing" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/list_backtest_scenarios.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
