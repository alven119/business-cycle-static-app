from __future__ import annotations

import subprocess
import sys


def test_show_phase57_boom_to_recession_transition_surface_completion_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase57_boom_to_recession_transition_surface_completion_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase57_boom_to_recession_transition_surface_completion_ready=True" in result.stdout
    assert "declared_current_phase=boom" in result.stdout
    assert "legal_next_phase=recession" in result.stdout
    assert "candidate_phase_emitted=False" in result.stdout
    assert "current_phase_emitted=False" in result.stdout
