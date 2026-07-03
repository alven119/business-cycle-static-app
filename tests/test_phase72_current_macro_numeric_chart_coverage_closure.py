from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase72_current_macro_numeric_chart_coverage_closure import (
    summarize_phase72_current_macro_numeric_chart_coverage_closure,
)


def test_phase72_current_macro_numeric_chart_coverage_closure_passes() -> None:
    summary = summarize_phase72_current_macro_numeric_chart_coverage_closure()

    assert summary["result"] == "passed"
    assert summary["phase72_current_macro_numeric_chart_coverage_ready"] is True
    assert summary["current_macro_numeric_chart_coverage_ready"] is True
    assert summary["role_count"] == 39
    assert summary["role_with_official_series_count"] == 37
    assert summary["role_without_official_series_count"] == 2
    assert summary["role_with_numeric_context_count"] == 37
    assert summary["role_with_available_chart_payload_count"] == 37
    assert summary["chart_unavailable_role_count"] == 2
    assert summary["fixture_cache_written_under_tmp"] is True
    assert summary["repo_output_written_count"] == 0
    assert summary["fixture_mislabeled_as_live_count"] == 0
    assert summary["point_in_time_claim_count"] == 0
    assert summary["numeric_context_promoted_to_phase_support_count"] == 0
    assert summary["missing_value_treated_as_neutral_count"] == 0
    assert summary["unavailable_chart_treated_as_zero_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["phase72_closure_status"] == (
        "closed_current_macro_numeric_chart_coverage_expanded_"
        "declared_state_preserved"
    )


def test_show_phase72_current_macro_numeric_chart_coverage_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase72_current_macro_numeric_chart_coverage_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase72_current_macro_numeric_chart_coverage_ready=true" in completed.stdout
    assert "role_with_available_chart_payload_count=37" in completed.stdout
    assert "fixture_cache_written_under_tmp=true" in completed.stdout
    assert "result=passed" in completed.stdout
