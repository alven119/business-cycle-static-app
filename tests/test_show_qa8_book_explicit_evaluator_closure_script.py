from __future__ import annotations

import subprocess
import sys


def test_show_qa8_book_explicit_evaluator_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_qa8_book_explicit_evaluator_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "recommended_next_phase=QA9" in result.stdout
    assert (
        "qa8_closure_status=closed_book_explicit_evaluators_frozen_forward_protocol_registered_not_started"
        in result.stdout
    )
