from __future__ import annotations

import subprocess
import sys


def test_show_phase54_low_cost_macro_source_completion_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase54_low_cost_macro_source_completion_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "phase54_low_cost_macro_source_completion_ready=true" in result.stdout
    assert "macromicro_api_candidate_count=0" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout
    assert "current_phase_emitted=false" in result.stdout
