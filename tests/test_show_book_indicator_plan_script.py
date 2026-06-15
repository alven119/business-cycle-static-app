from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_book_indicator_plan_script_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "batch_count=3" in completed.stdout
    assert "candidate_indicator_count=" in completed.stdout
    assert "high_priority_count=" in completed.stdout
    assert "purpose_groups=" in completed.stdout
    assert "continuing_jobless_claims" in completed.stdout
    assert "next_phases=7F1,7F2,7F3,8A" in completed.stdout


def test_show_book_indicator_plan_script_accepts_custom_plan(tmp_path: Path) -> None:
    source = Path("specs/backtests/book_aligned_indicator_implementation_plan.yaml")
    custom = tmp_path / "book_aligned_indicator_implementation_plan.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--plan", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout


def test_show_book_indicator_plan_missing_plan_fails(tmp_path: Path) -> None:
    completed = run_script("--plan", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Book-aligned indicator implementation plan file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_book_indicator_plan.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
