from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_transition_evidence_badge_renderer_contract_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "direct_trade_text_blocked=true" in completed.stdout
    assert "phase_override_field_blocked=true" in completed.stdout
    assert "dashboard_renderer_wiring_allowed_now=false" in completed.stdout
    assert "recommended_next_phase=7G4" in completed.stdout


def test_show_transition_evidence_badge_renderer_contract_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")
    custom = tmp_path / "renderer_contract.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=7G4" in completed.stdout


def test_show_transition_evidence_badge_renderer_contract_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--contract", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Transition evidence badge renderer contract file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_transition_evidence_badge_renderer_contract.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
