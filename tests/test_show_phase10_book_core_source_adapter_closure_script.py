from __future__ import annotations

import subprocess
import sys


def test_show_phase10_book_core_source_adapter_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase10_book_core_source_adapter_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "new_adapter_implemented_count=11" in result.stdout
    assert "new_forward_capture_ready_role_count=11" in result.stdout
    assert "prospective_track_next_action=WAIT_FOR_FIRST_ELIGIBLE_AS_OF" in result.stdout
