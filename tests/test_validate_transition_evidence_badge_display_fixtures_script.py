from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_transition_evidence_badge_display_fixtures_outputs_passed_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "valid_display_fixture_count=3" in completed.stdout
    assert "invalid_display_fixture_count=10" in completed.stdout
    assert "valid_display_pass_count=3" in completed.stdout
    assert "invalid_display_rejected_count=10" in completed.stdout
    assert "unexpected_valid_display_failures=0" in completed.stdout
    assert "unexpected_invalid_display_passes=0" in completed.stdout
    assert "expected_display_error_mismatches=0" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_display_fixtures_accepts_custom_contract(
    tmp_path: Path,
) -> None:
    source = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")
    custom = tmp_path / "renderer_contract.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--contract", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "contract_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_display_fixtures_accepts_custom_fixtures(
    tmp_path: Path,
) -> None:
    source = Path("specs/common/transition_evidence_badge_display_fixtures.yaml")
    custom = tmp_path / "display_fixtures.yaml"
    custom.write_text(
        source.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--fixtures", str(custom))

    assert completed.returncode == 0, completed.stderr
    assert "fixtures_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_display_fixtures_missing_path_fails(
    tmp_path: Path,
) -> None:
    completed = run_script("--fixtures", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Transition evidence badge display fixtures file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/validate_transition_evidence_badge_display_fixtures.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
