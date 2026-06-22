from __future__ import annotations

import subprocess
import sys


def test_show_qa9_prospective_shadow_registry_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_qa9_prospective_shadow_registry_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "recommended_next_phase=QA10" in result.stdout
    assert (
        "qa9_closure_status=closed_forward_registry_armed_not_started_candidate_capability_incomplete"
        in result.stdout
    )
