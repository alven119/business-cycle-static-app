from __future__ import annotations

from business_cycle.audits.phase60_evidence_freshness_release_value_continuity_closure import (
    summarize_phase60_evidence_freshness_release_value_continuity_closure,
)


def test_phase60_evidence_freshness_release_value_continuity_closure_passes() -> None:
    summary = summarize_phase60_evidence_freshness_release_value_continuity_closure()

    assert summary["result"] == "passed"
    assert summary["phase60_evidence_freshness_release_value_continuity_ready"] is True
    assert summary["evidence_freshness_release_value_continuity_ready"] is True
    assert summary["dashboard_evidence_continuity_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["continuity_card_count"] == 39
    assert summary["transition_continuity_context_count"] == 4
    assert summary["transition_lane_context_count"] == 13
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert (
        summary["phase60_closure_status"]
        == "closed_evidence_freshness_release_value_continuity_ready_no_phase_emission"
    )


def test_phase60_closure_keeps_phase59_start_confirmation_deferred() -> None:
    summary = summarize_phase60_evidence_freshness_release_value_continuity_closure()

    assert summary["phase59_declared_start_governance_deferred"] is True
    assert summary["declared_phase_age_false_precision_count"] == 0
    assert (
        "governed declared boom start date and phase-age confirmation remain open"
        in summary["deferred_capability_gaps"]
    )
    assert (
        summary["next_recommended_phase"]
        == "Phase61_major_group_evidence_profile_and_readiness_explanation"
    )
