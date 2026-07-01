from __future__ import annotations

from business_cycle.audits.phase55_macro_indicator_coverage_readiness_closure import (
    summarize_phase55_macro_indicator_coverage_readiness_closure,
)


def test_phase55_macro_indicator_coverage_readiness_closure_passes() -> None:
    summarize_phase55_macro_indicator_coverage_readiness_closure.cache_clear()
    summary = summarize_phase55_macro_indicator_coverage_readiness_closure()

    assert summary["result"] == "passed"
    assert summary["phase55_macro_indicator_coverage_readiness_ready"] is True
    assert summary["macro_indicator_coverage_readiness_matrix_ready"] is True
    assert summary["dashboard_gap_burn_down_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["coverage_role_count"] == 39
    assert summary["phase_with_coverage_count"] == 4
    assert summary["supporting_proxy_only_count"] == 3
    assert summary["user_authorized_input_required_count"] == 2
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["next_recommended_phase"] == (
        "Phase56_indicator_detail_source_risk_and_value_rendering"
    )
    assert summary["phase55_closure_status"] == (
        "closed_macro_indicator_coverage_readiness_matrix_ready_no_phase_emission"
    )
