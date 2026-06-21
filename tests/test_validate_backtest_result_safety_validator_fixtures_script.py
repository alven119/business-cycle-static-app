from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/validate_backtest_result_safety_validator_fixtures.py")
CONTRACT_PATH = Path("specs/portfolio/backtest_result_safety_validator_contract.yaml")
FIXTURES_PATH = Path("specs/portfolio/backtest_result_safety_validator_fixtures.yaml")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_validate_backtest_result_safety_validator_fixtures_script_succeeds() -> None:
    result = _run_script()

    assert result.returncode == 0
    assert "valid_result_fixture_count=" in result.stdout
    assert "invalid_result_fixture_count=" in result.stdout
    assert "valid_pass_count=" in result.stdout
    assert "invalid_rejected_count=" in result.stdout
    assert "unexpected_valid_failures=0" in result.stdout
    assert "unexpected_invalid_passes=0" in result.stdout
    assert "expected_error_mismatches=0" in result.stdout
    assert "public_output_written=false" in result.stdout
    assert "data_backtests_output_written=false" in result.stdout
    assert "output_written=false" in result.stdout
    assert "allocation_output_generated=false" in result.stdout
    assert "trade_signal_generated=false" in result.stdout
    assert "result=passed" in result.stdout
    assert not Path("data/backtests/research").exists()


def test_validate_backtest_result_safety_validator_fixtures_script_accepts_custom_paths() -> None:
    result = _run_script(
        "--contract",
        str(CONTRACT_PATH),
        "--fixtures",
        str(FIXTURES_PATH),
    )

    assert result.returncode == 0
    assert "result=passed" in result.stdout


def test_validate_backtest_result_safety_validator_fixtures_script_missing_fixtures_fails() -> None:
    result = _run_script("--fixtures", "specs/portfolio/missing_fixtures.yaml")

    assert result.returncode != 0
    assert "does not exist" in result.stderr
