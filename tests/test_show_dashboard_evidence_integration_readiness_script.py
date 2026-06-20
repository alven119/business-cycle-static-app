from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_dashboard_evidence_integration_readiness_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "dashboard_wiring_allowed_now=false" in completed.stdout
    assert "public_output_allowed_now=false" in completed.stdout
    assert "formal_decision_impact_allowed=false" in completed.stdout
    assert "phase_7g_closure_status=ready_to_close_after_validation" in completed.stdout
    assert "recommended_next_phase=8A" in completed.stdout


def test_show_dashboard_evidence_integration_readiness_accepts_custom_path(
    tmp_path: Path,
) -> None:
    source = Path("specs/common/dashboard_evidence_integration_readiness.yaml")
    custom = tmp_path / "readiness.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test", 1),
        encoding="utf-8",
    )

    completed = run_script("--readiness", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=8A" in completed.stdout


def test_show_dashboard_evidence_integration_readiness_missing_path_fails(
    tmp_path: Path,
) -> None:
    completed = run_script("--readiness", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Dashboard evidence integration readiness file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_dashboard_evidence_integration_readiness.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
