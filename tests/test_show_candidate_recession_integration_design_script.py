from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_candidate_recession_integration_design_script_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "hard_gate_allowed=false" in completed.stdout
    assert "soft_filter_allowed=true" in completed.stdout
    assert "diagnostic_only_allowed=true" in completed.stdout
    assert "required_acceptance_count=6" in completed.stdout
    assert "recommended_next_phase=7F2" in completed.stdout


def test_show_candidate_recession_integration_design_script_accepts_custom_design(
    tmp_path: Path,
) -> None:
    source = Path("specs/backtests/candidate_recession_integration_design.yaml")
    custom = tmp_path / "candidate_recession_integration_design.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--design", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout


def test_show_candidate_recession_integration_design_missing_design_fails(
    tmp_path: Path,
) -> None:
    completed = run_script("--design", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Candidate recession integration design file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_candidate_recession_integration_design.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
