from __future__ import annotations

from business_cycle.audits.phase57_boom_to_recession_transition_surface_completion_closure import (
    summarize_phase57_boom_to_recession_transition_surface_completion_closure,
)


def test_phase57_boom_to_recession_transition_surface_completion_closure_passes() -> None:
    summary = summarize_phase57_boom_to_recession_transition_surface_completion_closure()

    assert summary["result"] == "passed"
    assert summary["phase57_boom_to_recession_transition_surface_completion_ready"] is True
    assert summary["boom_to_recession_transition_surface_completion_ready"] is True
    assert summary["dashboard_transition_surface_completion_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert (
        summary["phase57_closure_status"]
        == "closed_boom_to_recession_transition_surface_completed_no_phase_emission"
    )
