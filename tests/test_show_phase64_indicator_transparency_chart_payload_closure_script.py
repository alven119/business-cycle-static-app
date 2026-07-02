from __future__ import annotations

import subprocess
import sys


def test_show_phase64_indicator_transparency_chart_payload_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase64_indicator_transparency_chart_payload_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase64_indicator_transparency_chart_payload_ready=True" in result.stdout
    assert "role_payload_count=39" in result.stdout
    assert "rendered_score_transparency_count=39" in result.stdout
    assert (
        "phase64_closure_status=closed_indicator_transparency_chart_payload_ready_no_phase_selection"
        in result.stdout
    )
