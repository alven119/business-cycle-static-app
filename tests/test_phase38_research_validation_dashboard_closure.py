from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase38_research_validation_dashboard_closure import (
    summarize_phase38_research_validation_dashboard_closure,
)


def test_phase38_research_validation_dashboard_closure_passes() -> None:
    summary = summarize_phase38_research_validation_dashboard_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["scenario_count"] == 5
    assert summary["comparable_scenario_count"] == 2
    assert summary["non_comparable_scenario_count"] == 3
    assert summary["remaining_pit_role_gap_count"] == 6
    assert summary["rule_unresolved_gap_count"] == 1
    assert summary["artifact_consistency_error_count"] == 0
    assert summary["alpha35_freeze_hash_valid"] is True
    assert summary["alpha34_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "historical_validation_research_dashboard_available_partial_"
        "comparability_no_performance"
    )
    assert summary["phase38_dashboard_status"] == "local_research_dashboard_operational"
    assert summary["development_next_phase"] == 39
    assert summary["phase38_closure_status"] == (
        "closed_research_validation_dashboard_operational_partial_comparability_"
        "no_performance"
    )


def test_show_phase38_research_validation_dashboard_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase38_research_validation_dashboard_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase38_closure_status=" in result.stdout
    assert "result=passed" in result.stdout
