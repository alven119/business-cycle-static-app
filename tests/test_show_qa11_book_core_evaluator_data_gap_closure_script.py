from __future__ import annotations

import subprocess
import sys


def test_show_qa11_book_core_evaluator_data_gap_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_qa11_book_core_evaluator_data_gap_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "candidate_capability_ready=false" in result.stdout
    assert "recommended_next_phase=QA12" in result.stdout
