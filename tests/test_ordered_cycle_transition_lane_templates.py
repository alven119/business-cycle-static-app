from __future__ import annotations

from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_template_view_model,
    build_full_ordered_cycle_transition_lane_templates,
    summarize_full_ordered_cycle_transition_lane_templates,
)


def test_full_ordered_cycle_transition_lane_templates_pass() -> None:
    artifact = build_full_ordered_cycle_transition_lane_templates()

    assert artifact["result"] == "passed"
    assert artifact["legal_transition_template_count"] == 4
    assert artifact["legal_transition_template_with_state_machine_match_count"] == 4
    assert artifact["lane_template_count"] == 13
    assert artifact["continuation_lane_template_count"] == 4
    assert artifact["watch_lane_template_count"] == 5
    assert artifact["confirmation_lane_template_count"] == 4


def test_full_ordered_cycle_transition_lane_templates_preserve_boundaries() -> None:
    summary = summarize_full_ordered_cycle_transition_lane_templates()

    assert summary["full_ordered_cycle_transition_lane_templates_ready"] is True
    assert summary["legal_cycle_order_valid"] is True
    assert summary["transition_with_continuation_lane_count"] == 4
    assert summary["transition_with_watch_lane_count"] == 4
    assert summary["transition_with_confirmation_lane_count"] == 4
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["supporting_only_role_replacement_allowed_count"] == 0


def test_full_ordered_cycle_transition_lane_templates_do_not_emit_decisions() -> None:
    summary = summarize_full_ordered_cycle_transition_lane_templates()

    assert summary["prohibited_output_field_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_full_ordered_cycle_transition_lane_template_view_model_is_research_only() -> None:
    view_model = build_full_ordered_cycle_transition_lane_template_view_model()

    assert view_model["view_id"] == "full_ordered_cycle_transition_lane_templates"
    assert (
        view_model["output_mode"]
        == "research_only_full_ordered_cycle_transition_lane_templates"
    )
    assert view_model["research_only"] is True
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert len(view_model["transition_templates"]) == 4
