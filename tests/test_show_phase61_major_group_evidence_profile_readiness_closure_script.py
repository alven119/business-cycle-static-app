from __future__ import annotations

import subprocess
import sys


def test_show_phase61_major_group_evidence_profile_readiness_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase61_major_group_evidence_profile_readiness_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase61_major_group_evidence_profile_readiness_ready=True" in result.stdout
    assert (
        "phase61_closure_status=closed_major_group_evidence_profiles_ready_no_phase_emission"
        in result.stdout
    )
