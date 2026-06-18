from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_boom_ending_refinement_plan_script_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "diagnosed_issue_count=4" in completed.stdout
    assert "proposed_refinement_count=5" in completed.stdout
    assert "high_priority_refinement_count=3" in completed.stdout
    assert "recommended_next_phase=7F2.3" in completed.stdout


def test_show_boom_ending_refinement_plan_accepts_custom_plan(tmp_path: Path) -> None:
    source = Path("specs/backtests/boom_ending_refinement_plan.yaml")
    custom = tmp_path / "boom_ending_refinement_plan.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--plan", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout


def test_show_boom_ending_refinement_plan_missing_plan_fails(tmp_path: Path) -> None:
    completed = run_script("--plan", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Boom ending refinement plan file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_boom_ending_refinement_plan.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
