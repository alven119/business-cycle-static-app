from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase37_recession_recovery_pit_remediation_closure import (
    summarize_phase37_recession_recovery_pit_remediation_closure,
)


def test_phase37_recession_recovery_pit_remediation_closure_passes() -> None:
    summary = summarize_phase37_recession_recovery_pit_remediation_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["post_insufficient_point_in_time_role_gap_count"] == 6
    assert summary["pre_insufficient_point_in_time_scenario_role_gap_count"] == 39
    assert summary["post_insufficient_point_in_time_scenario_role_gap_count"] == 16
    assert summary["phase37_clean_environment_deterministic"] is True
    assert summary["scenario_role_gap_row_count_fields_separated"] is True
    assert summary["pre_comparable_scenario_count"] == 2
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["false_comparability_count"] == 0
    assert summary["alpha34_freeze_hash_valid"] is True
    assert summary["alpha33_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "recession_recovery_pit_remediation_attempted_research_only_no_performance"
    )
    assert summary["development_next_phase"] == 38
    assert summary["phase37_closure_status"] == (
        "closed_recession_recovery_pit_remediation_reduced_pit_gaps_no_false_"
        "comparability"
    )


def test_show_phase37_recession_recovery_pit_remediation_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase37_recession_recovery_pit_remediation_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase37_closure_status=" in result.stdout
    assert "result=passed" in result.stdout
