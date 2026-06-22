from __future__ import annotations

import subprocess
import sys


def test_show_qa5_book_core_shadow_model_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_qa5_book_core_shadow_model_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in completed.stdout
    assert "proposed_v2_economically_validated=false" in completed.stdout
    assert "recommended_next_phase=QA6" in completed.stdout
