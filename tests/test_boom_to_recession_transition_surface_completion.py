from __future__ import annotations

from business_cycle.render.boom_to_recession_transition_surface import (
    build_boom_to_recession_transition_surface_completion,
    build_boom_to_recession_transition_surface_view_model,
    summarize_boom_to_recession_transition_surface_completion,
)


def test_boom_to_recession_transition_surface_completion_passes() -> None:
    surface = build_boom_to_recession_transition_surface_completion()

    assert surface["result"] == "passed"
    assert surface["declared_current_phase"] == "boom"
    assert surface["legal_next_phase"] == "recession"
    assert surface["transition_lane_count"] == 4
    assert surface["continuation_lane_count"] == 1
    assert surface["watch_lane_count"] == 2
    assert surface["confirmation_lane_count"] == 1
    assert surface["transition_priority_indicator_count"] == 5
    assert surface["transition_priority_indicator_with_detail_count"] == 5
    assert surface["full_macro_indicator_detail_count"] == 39


def test_boom_to_recession_transition_surface_preserves_lane_boundaries() -> None:
    summary = summarize_boom_to_recession_transition_surface_completion()

    assert summary["boom_to_recession_transition_surface_completion_ready"] is True
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["recession_confirmation_not_derived_from_watch_only"] is True
    assert summary["watch_promoted_to_confirmation_count"] == 0
    assert summary["confirmation_derived_from_watch_only_count"] == 0
    assert summary["boom_ending_watch_mislabeled_confirmation_count"] == 0
    assert summary["recession_watch_mislabeled_confirmation_count"] == 0
    assert summary["continuation_mislabeled_transition_count"] == 0


def test_boom_to_recession_transition_surface_uses_indicator_details() -> None:
    surface = build_boom_to_recession_transition_surface_completion()

    assert surface["source_risk_visible_priority_count"] == 5
    assert surface["value_context_visible_priority_count"] == 5
    assert surface["freshness_context_visible_priority_count"] == 5
    assert surface["release_timing_context_visible_priority_count"] == 5
    assert surface["why_not_evidence_visible_priority_count"] == 5
    assert surface["missing_or_abstention_reason_visible_priority_count"] == 5
    assert all(
        card["phase56_detail_card_linked"]
        for card in surface["priority_indicator_cards"]
    )


def test_boom_to_recession_transition_surface_has_no_decision_outputs() -> None:
    summary = summarize_boom_to_recession_transition_surface_completion()

    assert summary["prohibited_output_field_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_boom_to_recession_transition_surface_view_model_is_research_only() -> None:
    view_model = build_boom_to_recession_transition_surface_view_model()

    assert view_model["view_id"] == "boom_to_recession_transition_surface_completion"
    assert (
        view_model["output_mode"]
        == "research_only_boom_to_recession_transition_surface"
    )
    assert view_model["research_only"] is True
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
