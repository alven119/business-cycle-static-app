from __future__ import annotations

import subprocess
import sys


def test_show_phase11_book_core_phase_evidence_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase11_book_core_phase_evidence_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "north_star_contract_valid=true" in result.stdout
    assert "candidate_selection_enabled=false" in result.stdout
