from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/show_backtest_result_writer_contract.py")
CONTRACT_PATH = Path("specs/portfolio/backtest_result_writer_contract.yaml")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_show_backtest_result_writer_contract_script_succeeds() -> None:
    result = _run_script()

    assert result.returncode == 0
    assert "explicit_user_command_required=true" in result.stdout
    assert "automatic_write_allowed=false" in result.stdout
    assert "implement_writer_runtime_allowed=false" in result.stdout
    assert "write_result_files_allowed=false" in result.stdout
    assert "create_output_directories_allowed=false" in result.stdout
    assert "write_data_backtests_output_allowed=false" in result.stdout
    assert "write_public_output_allowed=false" in result.stdout
    assert "writer_runtime_allowed_now=false" in result.stdout
    assert "result_file_write_allowed_now=false" in result.stdout
    assert "recommended_next_phase=9A8" in result.stdout
    assert not Path("data/backtests/research").exists()


def test_show_backtest_result_writer_contract_script_accepts_custom_path() -> None:
    result = _run_script("--contract", str(CONTRACT_PATH))

    assert result.returncode == 0
    assert "recommended_next_phase=9A8" in result.stdout


def test_show_backtest_result_writer_contract_script_missing_path_fails() -> None:
    result = _run_script("--contract", "specs/portfolio/missing_writer_contract.yaml")

    assert result.returncode != 0
    assert "does not exist" in result.stderr
