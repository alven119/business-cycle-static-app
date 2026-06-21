from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_run_portfolio_backtest_structural_dry_run_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "dry_run_count=3" in completed.stdout
    assert "valid_dry_run_count=3" in completed.stdout
    assert "invalid_dry_run_count=0" in completed.stdout
    assert "performance_metrics_computed=false" in completed.stdout
    assert "output_written=false" in completed.stdout
    assert "data_backtests_output_written=false" in completed.stdout
    assert "public_output_written=false" in completed.stdout
    assert "allocation_output_generated=false" in completed.stdout
    assert "trade_signal_generated=false" in completed.stdout
    assert "result=passed" in completed.stdout


def test_run_portfolio_backtest_structural_dry_run_accepts_custom_contract(tmp_path: Path) -> None:
    custom = copy_with_status(
        Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml"),
        tmp_path / "portfolio_backtest_dry_run_contract.yaml",
    )

    completed = run_script("--contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "result=passed" in completed.stdout


def test_run_portfolio_backtest_structural_dry_run_accepts_custom_input_contract(tmp_path: Path) -> None:
    custom = copy_with_status(
        Path("specs/portfolio/portfolio_backtest_input_contract.yaml"),
        tmp_path / "portfolio_backtest_input_contract.yaml",
    )

    completed = run_script("--input-contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "result=passed" in completed.stdout


def test_run_portfolio_backtest_structural_dry_run_accepts_custom_mapping(tmp_path: Path) -> None:
    custom = copy_with_status(
        Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml"),
        tmp_path / "portfolio_backtest_scenario_mapping.yaml",
    )

    completed = run_script("--mapping", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "result=passed" in completed.stdout


def test_run_portfolio_backtest_structural_dry_run_accepts_custom_fixtures(tmp_path: Path) -> None:
    custom = copy_with_status(
        Path("specs/portfolio/portfolio_backtest_input_fixtures.yaml"),
        tmp_path / "portfolio_backtest_input_fixtures.yaml",
    )

    completed = run_script("--fixtures", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "result=passed" in completed.stdout


def test_run_portfolio_backtest_structural_dry_run_missing_fixtures_fails(tmp_path: Path) -> None:
    completed = run_script("--fixtures", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "result=failed" in completed.stdout
    assert "portfolio_backtest_input_fixtures file does not exist" in completed.stderr


def copy_with_status(source: Path, target: Path) -> Path:
    target.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )
    return target


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_portfolio_backtest_structural_dry_run.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
