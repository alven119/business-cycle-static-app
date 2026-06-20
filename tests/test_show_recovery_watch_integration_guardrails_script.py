from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_recovery_watch_integration_guardrails_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "diagnostic_only_allowed=true" in completed.stdout
    assert "recovery_evidence_display_allowed=true" in completed.stdout
    assert "transition_risk_adjustment_allowed=true" in completed.stdout
    assert "direct_recovery_confirmation_allowed=false" in completed.stdout
    assert "direct_portfolio_action_allowed=false" in completed.stdout
    assert "portfolio_policy_research_input_allowed=true" in completed.stdout
    assert "required_acceptance_count=8" in completed.stdout
    assert "recommended_next_phase=7G" in completed.stdout


def test_show_recovery_watch_integration_guardrails_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/backtests/recovery_watch_integration_guardrails.yaml")
    custom = tmp_path / "guardrails.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--guardrails", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=7G" in completed.stdout


def test_show_recovery_watch_integration_guardrails_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--guardrails", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Recovery watch integration guardrails file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_recovery_watch_integration_guardrails.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
