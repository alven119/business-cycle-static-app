from __future__ import annotations

from business_cycle.audits.phase50_transition_surface_data_risk_closure import (
    summarize_phase50_transition_surface_data_risk_closure,
)


def test_phase50_transition_surface_data_risk_closure_passes() -> None:
    summarize_phase50_transition_surface_data_risk_closure.cache_clear()
    summary = summarize_phase50_transition_surface_data_risk_closure()

    assert summary["result"] == "passed"
    assert summary["phase50_transition_surface_data_risk_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["data_risk_label_present_count"] == 5
    assert summary["source_credibility_label_present_count"] == 5
    assert summary["alternative_source_candidate_card_count"] == 5
    assert summary["substitution_degree_visible_count"] == 5
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["next_recommended_phase"] == (
        "Phase51_declared_boom_start_date_governance"
    )
