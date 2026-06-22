from __future__ import annotations

import subprocess
import sys


def test_show_qa12_major_group_manual_start_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_qa12_major_group_manual_start_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "recommended_next_action=WAIT_FOR_FIRST_ELIGIBLE_AS_OF" in result.stdout
    assert "qa13_allowed_now=false" in result.stdout

