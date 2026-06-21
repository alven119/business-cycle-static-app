from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_real_backtest_prototype_readiness_gate_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "real_backtest_execution_allowed=false" in completed.stdout
    assert "performance_metrics_allowed=false" in completed.stdout
    assert "backtest_result_output_allowed=false" in completed.stdout
    assert "data_backtests_output_allowed=false" in completed.stdout
    assert "public_output_allowed=false" in completed.stdout
    assert "recommended_next_phase=9A" in completed.stdout


def test_show_real_backtest_prototype_readiness_gate_accepts_custom_path(
    tmp_path: Path,
) -> None:
    source = Path("specs/portfolio/real_backtest_prototype_readiness_gate.yaml")
    custom = tmp_path / "real_backtest_prototype_readiness_gate.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--gate", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=9A" in completed.stdout


def test_show_real_backtest_prototype_readiness_gate_missing_path_fails(
    tmp_path: Path,
) -> None:
    completed = run_script("--gate", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "real_backtest_prototype_readiness_gate file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_real_backtest_prototype_readiness_gate.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
