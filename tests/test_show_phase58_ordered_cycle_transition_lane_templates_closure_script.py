from __future__ import annotations

import subprocess
import sys


def test_show_phase58_ordered_cycle_transition_lane_templates_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase58_ordered_cycle_transition_lane_templates_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase58_ordered_cycle_transition_lane_templates_ready=True" in result.stdout
    assert "full_ordered_cycle_transition_lane_templates_ready=True" in result.stdout
    assert "legal_transition_template_count=4" in result.stdout
    assert "lane_template_count=13" in result.stdout
    assert "candidate_phase_emitted=False" in result.stdout
