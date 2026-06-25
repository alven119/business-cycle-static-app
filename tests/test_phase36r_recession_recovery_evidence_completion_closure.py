from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase36r_recession_recovery_evidence_completion_closure import (
    summarize_phase36r_recession_recovery_evidence_completion_closure,
)


def test_phase36r_recession_recovery_evidence_completion_closure_passes() -> None:
    summary = summarize_phase36r_recession_recovery_evidence_completion_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["phase_evidence_completion_attempted_scenario_count"] == 3
    assert summary["safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["false_comparability_count"] == 0
    assert summary["alpha33_freeze_hash_valid"] is True
    assert summary["alpha32_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "recession_recovery_evidence_completion_attempted_research_only_no_performance"
    )
    assert summary["development_next_phase"] == "PHASE_36R_REVIEW"
    assert summary["phase36r_closure_status"] == (
        "closed_recession_recovery_evidence_completion_attempted_remaining_genuine_"
        "non_comparable"
    )


def test_show_phase36r_recession_recovery_evidence_completion_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase36r_recession_recovery_evidence_completion_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase36r_closure_status=" in result.stdout
    assert "result=passed" in result.stdout
