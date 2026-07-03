from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_portfolio_policy_research_plan_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "template_count=3" in completed.stdout
    assert "live_allocation_allowed_now=false" in completed.stdout
    assert "trade_signal_generation_allowed_now=false" in completed.stdout
    assert "public_output_allowed_now=false" in completed.stdout
    assert "recommended_next_phase=8B" in completed.stdout


def test_show_portfolio_policy_research_plan_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/portfolio/portfolio_policy_research_plan.yaml")
    custom = tmp_path / "portfolio_policy_research_plan.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--plan", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=8B" in completed.stdout


def test_show_portfolio_policy_research_plan_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--plan", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Portfolio policy research plan file does not exist" in completed.stderr


def test_show_portfolio_policy_research_baseline_outputs_summary() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_portfolio_policy_research_baseline.py"],
        cwd=Path(__file__).resolve().parents[1],
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "portfolio_policy_research_baseline_contract_ready=true" in completed.stdout
    assert "required_policy_template_count=8" in completed.stdout
    assert "research_only_template_count=8" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_portfolio_policy_research_plan.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
