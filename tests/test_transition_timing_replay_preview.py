from __future__ import annotations

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview,
    build_transition_timing_replay_preview_view_model,
    summarize_transition_timing_replay_preview,
)


def test_transition_timing_replay_preview_passes_hard_gates() -> None:
    summary = summarize_transition_timing_replay_preview()

    assert summary["result"] == "passed"
    assert summary["transition_timing_replay_preview_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["transition_replay_checkpoint_count"] == 3
    assert summary["transition_template_count"] == 4
    assert summary["transition_lane_timing_preview_count"] == 13
    assert summary["evidence_accumulation_event_count"] == 39
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_transition_timing_replay_preview_preserves_doctrine_boundaries() -> None:
    artifact = build_transition_timing_replay_preview()

    assert artifact["prohibited_output_field_count"] == 0
    assert artifact["standalone_classifier_added_count"] == 0
    assert artifact["phase_rank_or_score_added_count"] == 0
    assert artifact["role_count_voting_added_count"] == 0
    assert artifact["historical_validation_executed"] is False
    assert artifact["backtest_execution_count"] == 0
    assert artifact["missing_value_treated_as_neutral_count"] == 0
    assert artifact["metadata_only_promoted_to_phase_support_count"] == 0
    assert all(
        event["watch_promoted_to_confirmation"] is False
        for event in artifact["evidence_accumulation_events"]
    )
    assert all(
        event["changes_declared_phase"] is False
        for event in artifact["evidence_accumulation_events"]
    )


def test_transition_timing_replay_preview_view_model_is_dashboard_ready() -> None:
    view_model = build_transition_timing_replay_preview_view_model()

    assert view_model["view_id"] == "transition_timing_replay_preview"
    assert view_model["research_only"] is True
    assert view_model["transition_replay_checkpoint_count"] == 3
    assert view_model["transition_lane_timing_preview_count"] == 13
    assert view_model["evidence_accumulation_event_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_research_dashboard_bundle_accepts_transition_timing_replay_preview() -> None:
    preview = build_transition_timing_replay_preview_view_model()
    bundle = build_research_dashboard_bundle(transition_timing_replay_preview=preview)
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "transition_timing_replay_preview" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["transition_timing_replay_preview"]["research_only"] is True
    assert bundle["transition_timing_replay_preview"]["candidate_phase_emitted"] is False
    assert bundle["transition_timing_replay_preview"]["current_phase_emitted"] is False
    assert validation["prohibited_action_field_count"] == 0
