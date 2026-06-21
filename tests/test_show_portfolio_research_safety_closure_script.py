from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_portfolio_research_safety_closure_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "research_only=true" in completed.stdout
    assert "structural_dry_run_only=true" in completed.stdout
    assert "formal_backtest_executed=false" in completed.stdout
    assert "performance_metrics_computed=false" in completed.stdout
    assert "allocation_output_generated=false" in completed.stdout
    assert "trade_signal_generated=false" in completed.stdout
    assert "data_backtests_output_written=false" in completed.stdout
    assert "public_output_written=false" in completed.stdout
    assert "recommended_next_phase=8I" in completed.stdout


def test_show_portfolio_research_safety_closure_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/portfolio/portfolio_research_safety_closure.yaml")
    custom = tmp_path / "portfolio_research_safety_closure.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--closure", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=8I" in completed.stdout


def test_show_portfolio_research_safety_closure_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--closure", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "portfolio_research_safety_closure file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_portfolio_research_safety_closure.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
