from __future__ import annotations

import subprocess
import sys


def test_run_prospective_shadow_observation_script_dry_run_no_write() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_prospective_shadow_observation.py",
            "--dry-run",
            "--metadata-only",
            "--no-write",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "record_written=false" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout


def test_run_prospective_shadow_observation_script_rejects_non_test_clock() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_prospective_shadow_observation.py",
            "--dry-run",
            "--metadata-only",
            "--no-write",
            "--clock-date",
            "2008-09-30",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "gate_status=rejected_noncanonical_as_of" in result.stdout
