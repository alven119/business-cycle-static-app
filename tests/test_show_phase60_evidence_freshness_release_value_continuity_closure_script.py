from __future__ import annotations

import subprocess
import sys


def test_show_phase60_evidence_freshness_release_value_continuity_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase60_evidence_freshness_release_value_continuity_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "phase60_evidence_freshness_release_value_continuity_ready=True"
        in result.stdout
    )
    assert (
        "phase60_closure_status=closed_evidence_freshness_release_value_continuity_ready_no_phase_emission"
        in result.stdout
    )
