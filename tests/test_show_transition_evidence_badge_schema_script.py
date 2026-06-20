from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_show_transition_evidence_badge_schema_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "version=1" in completed.stdout
    assert "status=draft" in completed.stdout
    assert "badge_family_count=3" in completed.stdout
    assert "dashboard_contract_allowed_now=false" in completed.stdout
    assert "formal_decision_impact_allowed=false" in completed.stdout
    assert "direct_trade_signal_allowed=false" in completed.stdout
    assert "recommended_next_phase=7G2" in completed.stdout


def test_show_transition_evidence_badge_schema_accepts_custom_path(tmp_path: Path) -> None:
    source = Path("specs/common/transition_evidence_badge_schema.yaml")
    custom = tmp_path / "badge_schema.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--schema", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "status=test" in completed.stdout
    assert "recommended_next_phase=7G2" in completed.stdout


def test_show_transition_evidence_badge_schema_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--schema", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Transition evidence badge schema file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/show_transition_evidence_badge_schema.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
