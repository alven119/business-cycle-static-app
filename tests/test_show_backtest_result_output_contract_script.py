from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_backtest_result_output_contract_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "produce_backtest_results_allowed=false" in completed.stdout
    assert "compute_metric_values_allowed=false" in completed.stdout
    assert "write_result_files_allowed=false" in completed.stdout
    assert "write_data_backtests_output_allowed=false" in completed.stdout
    assert "write_public_output_allowed=false" in completed.stdout
    assert "metric_values_allowed_now=false" in completed.stdout
    assert "recommended_next_phase=9A2" in completed.stdout


def test_show_backtest_result_output_contract_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/portfolio/backtest_result_output_contract.yaml")
    custom = tmp_path / "backtest_result_output_contract.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=9A2" in completed.stdout


def test_show_backtest_result_output_contract_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--contract", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "backtest_result_output_contract file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_backtest_result_output_contract.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
