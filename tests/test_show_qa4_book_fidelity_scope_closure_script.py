from __future__ import annotations

import subprocess
import sys


def test_show_qa4_book_fidelity_scope_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_qa4_book_fidelity_scope_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in completed.stdout
    assert "recommended_next_phase=QA5" in completed.stdout

