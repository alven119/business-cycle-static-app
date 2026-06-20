from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_transition_evidence_badge_fixtures_outputs_passed_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "valid_fixture_count=3" in completed.stdout
    assert "invalid_fixture_count=7" in completed.stdout
    assert "valid_pass_count=3" in completed.stdout
    assert "invalid_rejected_count=7" in completed.stdout
    assert "unexpected_valid_failures=0" in completed.stdout
    assert "unexpected_invalid_passes=0" in completed.stdout
    assert "expected_error_mismatches=0" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_fixtures_accepts_custom_schema(tmp_path: Path) -> None:
    source_schema = Path("specs/common/transition_evidence_badge_schema.yaml")
    custom_schema = tmp_path / "badge_schema.yaml"
    custom_schema.write_text(
        source_schema.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--schema", str(custom_schema))

    assert completed.returncode == 0, completed.stderr
    assert "schema_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_fixtures_accepts_custom_fixtures(tmp_path: Path) -> None:
    source_fixtures = Path("specs/common/transition_evidence_badge_fixtures.yaml")
    custom_fixtures = tmp_path / "badge_fixtures.yaml"
    custom_fixtures.write_text(
        source_fixtures.read_text(encoding="utf-8").replace("status: draft", "status: test"),
        encoding="utf-8",
    )

    completed = run_script("--fixtures", str(custom_fixtures))

    assert completed.returncode == 0, completed.stderr
    assert "fixtures_version=1" in completed.stdout
    assert "result=passed" in completed.stdout


def test_validate_transition_evidence_badge_fixtures_missing_path_fails(tmp_path: Path) -> None:
    completed = run_script("--fixtures", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Transition evidence badge fixtures file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/validate_transition_evidence_badge_fixtures.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
