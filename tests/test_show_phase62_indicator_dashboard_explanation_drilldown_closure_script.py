from __future__ import annotations

import subprocess
import sys


def test_show_phase62_indicator_dashboard_explanation_drilldown_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase62_indicator_dashboard_explanation_drilldown_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase62_indicator_dashboard_explanation_drilldown_ready=True" in result.stdout
    assert (
        "phase62_closure_status=closed_indicator_dashboard_explanation_drilldown_ready_no_phase_emission"
        in result.stdout
    )
