from __future__ import annotations

import subprocess
import sys


def test_show_phase63_latest_evidence_dashboard_wiring_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase63_latest_evidence_dashboard_wiring_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase63_latest_evidence_dashboard_wiring_ready=True" in result.stdout
    assert "latest_evidence_dashboard_page_ready=True" in result.stdout
    assert "major_group_drilldown_rendered_count=24" in result.stdout
    assert "role_drilldown_rendered_count=39" in result.stdout
    assert (
        "phase63_closure_status=closed_latest_evidence_dashboard_wired_no_phase_selection"
        in result.stdout
    )
