from __future__ import annotations

import subprocess
import sys


def test_show_phase55_macro_indicator_coverage_readiness_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase55_macro_indicator_coverage_readiness_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase55_macro_indicator_coverage_readiness_ready=true" in result.stdout
    assert "dashboard_gap_burn_down_view_ready=true" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout
    assert "current_phase_emitted=false" in result.stdout
