from __future__ import annotations

from business_cycle.audits.phase58_ordered_cycle_transition_lane_templates_closure import (
    summarize_phase58_ordered_cycle_transition_lane_templates_closure,
)


def test_phase58_ordered_cycle_transition_lane_templates_closure_passes() -> None:
    summary = summarize_phase58_ordered_cycle_transition_lane_templates_closure()

    assert summary["result"] == "passed"
    assert summary["phase58_ordered_cycle_transition_lane_templates_ready"] is True
    assert summary["full_ordered_cycle_transition_lane_templates_ready"] is True
    assert summary["dashboard_ordered_cycle_transition_template_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["legal_transition_template_count"] == 4
    assert summary["lane_template_count"] == 13
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert (
        summary["phase58_closure_status"]
        == "closed_full_ordered_cycle_transition_lane_templates_ready_no_phase_emission"
    )
