from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase35_historical_comparability_realization_closure import (
    summarize_phase35_historical_comparability_realization_closure,
)


def test_phase35_historical_comparability_realization_closure_passes() -> None:
    summary = summarize_phase35_historical_comparability_realization_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["autonomous_comparability_realization_ready"] is True
    assert summary["post_comparability_validation_rerun_ready"] is True
    assert summary["historical_comparability_diagnostics_ready"] is True
    assert summary["pre_blocked_scenario_count"] == 0
    assert summary["post_blocked_scenario_count"] == 0
    assert summary["pre_comparable_scenario_count"] == 0
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["false_comparability_count"] == 0
    assert summary["alpha31_freeze_hash_valid"] is True
    assert summary["alpha30_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "historical_comparability_realization_attempted_research_only_no_performance"
    )
    assert summary["development_next_phase"] == 36
    assert summary["phase35_closure_status"] == (
        "closed_historical_comparability_realized_research_only_no_performance"
    )


def test_show_phase35_historical_comparability_realization_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase35_historical_comparability_realization_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase35_closure_status=" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
    assert "result=passed" in result.stdout
