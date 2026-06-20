from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_cycle_transition_evidence_architecture_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "evidence_family_count=3" in completed.stdout
    assert "dashboard_diagnostics_allowed_now=false" in completed.stdout
    assert "formal_phase_change_allowed_now=false" in completed.stdout
    assert "direct_trade_signal_allowed_now=false" in completed.stdout
    assert "recommended_next_phase=7G1" in completed.stdout


def test_show_cycle_transition_evidence_architecture_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/common/cycle_transition_evidence_architecture.yaml")
    custom = tmp_path / "architecture.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--architecture", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=7G1" in completed.stdout


def test_show_cycle_transition_evidence_architecture_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--architecture", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Cycle transition evidence architecture file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_cycle_transition_evidence_architecture.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
