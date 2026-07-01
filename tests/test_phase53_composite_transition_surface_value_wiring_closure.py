from __future__ import annotations

from business_cycle.audits.phase53_composite_transition_surface_value_wiring_closure import (
    summarize_phase53_composite_transition_surface_value_wiring_closure,
)


def test_phase53_composite_transition_surface_value_wiring_closure_passes() -> None:
    summarize_phase53_composite_transition_surface_value_wiring_closure.cache_clear()
    summary = summarize_phase53_composite_transition_surface_value_wiring_closure()

    assert summary["result"] == "passed"
    assert summary["phase53_composite_transition_surface_value_wiring_ready"] is True
    assert summary["composite_transition_surface_value_wiring_ready"] is True
    assert summary["boom_transition_dashboard_surface_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["role_count"] == 12
    assert summary["transition_surface_role_count"] == 5
    assert summary["composite_or_rule_gap_role_count"] == 7
    assert summary["source_metadata_ready_role_count"] == 12
    assert summary["value_context_visible_role_count"] == 12
    assert summary["surface_value_context_status_visible_count"] == 5
    assert summary["surface_composite_alignment_status_visible_count"] == 5
    assert summary["surface_phase53_explicit_abstention_reason_count"] == 5
    assert summary["phase_support_added_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["next_recommended_phase"] == (
        "Phase54_declared_boom_start_governance_and_indicator_detail_wiring"
    )
    assert summary["phase53_closure_status"] == (
        "closed_composite_transition_surface_value_context_ready_no_phase_emission"
    )
