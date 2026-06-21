from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/show_real_backtest_execution_readiness_closure.py")
CLOSURE_PATH = Path("specs/portfolio/real_backtest_execution_readiness_closure.yaml")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_show_real_backtest_execution_readiness_closure_script_succeeds() -> None:
    result = _run_script()

    assert result.returncode == 0
    assert "phase_9a_contract_stack_complete=true" in result.stdout
    assert "real_backtest_execution_allowed_now=false" in result.stdout
    assert "result_file_write_allowed_now=false" in result.stdout
    assert "output_directory_creation_allowed_now=false" in result.stdout
    assert "data_backtests_write_allowed_now=false" in result.stdout
    assert "public_write_allowed_now=false" in result.stdout
    assert "controlled_9b_prototype_entry_allowed=true" in result.stdout
    assert "default_9b_output_write_allowed=false" in result.stdout
    assert "recommended_next_phase=9B" in result.stdout
    assert not Path("data/backtests/research").exists()


def test_show_real_backtest_execution_readiness_closure_script_accepts_custom_path() -> None:
    result = _run_script("--closure", str(CLOSURE_PATH))

    assert result.returncode == 0
    assert "recommended_next_phase=9B" in result.stdout


def test_show_real_backtest_execution_readiness_closure_script_missing_path_fails() -> None:
    result = _run_script("--closure", "specs/portfolio/missing_execution_closure.yaml")

    assert result.returncode != 0
    assert "does not exist" in result.stderr
