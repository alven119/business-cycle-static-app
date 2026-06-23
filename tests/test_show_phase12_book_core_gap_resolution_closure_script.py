from __future__ import annotations

import subprocess
import sys


def test_show_phase12_book_core_gap_resolution_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase12_book_core_gap_resolution_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=12" in completed.stdout
    assert "remaining_gap_reviewed_count=9" in completed.stdout
    assert "gap_resolution_registry_ready=true" in completed.stdout
    assert "alpha8_freeze_hash_valid=true" in completed.stdout
    assert "phase12_closure_status=closed_remaining_book_core_gaps_reviewed" in (
        completed.stdout
    )
