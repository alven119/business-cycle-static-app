from __future__ import annotations

import subprocess
import sys


def test_show_phase53_composite_transition_surface_value_wiring_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase53_composite_transition_surface_value_wiring_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase53_composite_transition_surface_value_wiring_ready=true" in (
        completed.stdout
    )
    assert "candidate_phase_emitted=false" in completed.stdout
    assert "current_phase_emitted=false" in completed.stdout
