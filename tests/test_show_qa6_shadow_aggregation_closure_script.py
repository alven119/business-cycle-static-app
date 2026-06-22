from __future__ import annotations

import subprocess
import sys


def test_show_qa6_shadow_aggregation_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_qa6_shadow_aggregation_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in completed.stdout
    assert "candidate_selection_enabled=false" in completed.stdout
    assert "recommended_next_phase=QA7" in completed.stdout
