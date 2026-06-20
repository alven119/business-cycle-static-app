from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_portfolio_backtest_dry_run_fixtures_outputs_passed() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "valid_output_count=3" in completed.stdout
    assert "unexpected_invalid_passes=0" in completed.stdout
    assert "output_written=false" in completed.stdout
    assert "data_backtests_output_written=false" in completed.stdout
    assert "allocation_output_generated=false" in completed.stdout
    assert "trade_signal_generated=false" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_portfolio_backtest_dry_run_fixtures_accepts_custom_contract(tmp_path: Path) -> None:
    source = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")
    custom = tmp_path / "portfolio_backtest_dry_run_contract.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "contract_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_portfolio_backtest_dry_run_fixtures_accepts_custom_fixtures(tmp_path: Path) -> None:
    source = Path("specs/portfolio/portfolio_backtest_dry_run_fixtures.yaml")
    custom = tmp_path / "portfolio_backtest_dry_run_fixtures.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--fixtures", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "fixtures_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_portfolio_backtest_dry_run_fixtures_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--fixtures", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "portfolio_backtest_dry_run_fixtures file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/validate_portfolio_backtest_dry_run_fixtures.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
