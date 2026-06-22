from __future__ import annotations

import subprocess
import sys


def test_show_qa7_evidence_rule_candidate_freeze_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_qa7_evidence_rule_candidate_freeze_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in completed.stdout
    assert "recommended_next_phase=QA8" in completed.stdout
    assert "real_data_candidate_selection_enabled=false" in completed.stdout
