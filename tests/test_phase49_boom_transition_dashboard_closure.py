from __future__ import annotations

from business_cycle.audits.phase49_boom_transition_dashboard_closure import (
    summarize_phase49_boom_transition_dashboard_closure,
)


def test_phase49_boom_transition_dashboard_closure_passes() -> None:
    summarize_phase49_boom_transition_dashboard_closure.cache_clear()
    summary = summarize_phase49_boom_transition_dashboard_closure()

    assert summary["result"] == "passed"
    assert summary["phase49_dashboard_surface_ready"] is True
    assert summary["research_dashboard_boom_transition_view_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["indicator_card_count"] == 5
    assert summary["watch_confirmation_separation_visible"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
