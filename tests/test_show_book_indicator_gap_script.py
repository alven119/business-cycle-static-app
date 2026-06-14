from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_book_indicator_gap_script_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "group_count=4" in completed.stdout
    assert "gap_count=4" in completed.stdout
    assert "high_priority_count=" in completed.stdout
    assert "sensitivity_issue_count=4" in completed.stdout
    assert "phase_7e_breadth_confirmation" in completed.stdout


def test_show_book_indicator_gap_script_accepts_custom_spec(tmp_path: Path) -> None:
    source = Path("specs/backtests/book_indicator_gap_analysis.yaml")
    custom = tmp_path / "book_indicator_gap_analysis.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--spec", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout


def test_show_book_indicator_gap_missing_spec_fails(tmp_path: Path) -> None:
    completed = run_script("--spec", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Book indicator gap analysis file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_book_indicator_gap.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
