from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/run_controlled_real_backtest_prototype.py")
FIXTURES_PATH = Path("specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_run_controlled_real_backtest_prototype_script_succeeds() -> None:
    result = _run_script()

    assert result.returncode == 0
    assert "in_memory_only=true" in result.stdout
    assert "controlled_metric_computation_allowed=true" in result.stdout
    assert "result_file_written=false" in result.stdout
    assert "data_backtests_output_written=false" in result.stdout
    assert "public_output_written=false" in result.stdout
    assert "output_directory_created=false" in result.stdout
    assert "allocation_output_generated=false" in result.stdout
    assert "trade_signal_generated=false" in result.stdout
    assert "live_recommendation_generated=false" in result.stdout
    assert "dashboard_integration=false" in result.stdout
    assert "result=passed" in result.stdout
    assert "recommended_next_phase=9B1" in result.stdout
    assert not Path("data/backtests/research").exists()


def test_run_controlled_real_backtest_prototype_script_accepts_custom_path() -> None:
    result = _run_script("--fixtures", str(FIXTURES_PATH))

    assert result.returncode == 0
    assert "recommended_next_phase=9B1" in result.stdout


def test_run_controlled_real_backtest_prototype_script_missing_path_fails() -> None:
    result = _run_script("--fixtures", "specs/portfolio/missing_controlled_fixtures.yaml")

    assert result.returncode != 0
    assert "does not exist" in result.stderr


def test_run_controlled_real_backtest_prototype_stdout_has_no_prohibited_terms() -> None:
    result = _run_script()

    assert result.returncode == 0
    assert "target_weight" not in result.stdout
    assert "buy_signal" not in result.stdout
    assert "sell_signal" not in result.stdout
    assert "目前建議" not in result.stdout
    assert "建議買進" not in result.stdout
    assert "建議賣出" not in result.stdout
    assert not Path("data/backtests/research").exists()
