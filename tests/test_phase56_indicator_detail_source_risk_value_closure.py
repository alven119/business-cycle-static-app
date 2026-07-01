from __future__ import annotations

from business_cycle.audits.phase56_indicator_detail_source_risk_value_closure import (
    summarize_phase56_indicator_detail_source_risk_value_closure,
)


def test_phase56_indicator_detail_source_risk_value_closure_passes() -> None:
    summary = summarize_phase56_indicator_detail_source_risk_value_closure()

    assert summary["result"] == "passed"
    assert summary["phase56_indicator_detail_source_risk_value_ready"] is True
    assert summary["indicator_detail_source_risk_value_rendering_ready"] is True
    assert summary["dashboard_indicator_detail_view_ready"] is True
    assert summary["indicator_detail_card_count"] == 39
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["next_recommended_phase"] == (
        "Phase57_boom_to_recession_transition_surface_completion"
    )
    assert summary["phase56_closure_status"] == (
        "closed_indicator_detail_source_risk_value_rendering_ready_no_phase_emission"
    )
