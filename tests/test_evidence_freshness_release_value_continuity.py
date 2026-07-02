from __future__ import annotations

from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity,
    build_evidence_freshness_release_value_continuity_view_model,
    summarize_evidence_freshness_release_value_continuity,
)


def test_phase60_continuity_artifact_passes() -> None:
    summary = summarize_evidence_freshness_release_value_continuity()

    assert summary["result"] == "passed"
    assert summary["evidence_freshness_release_value_continuity_ready"] is True
    assert summary["continuity_card_count"] == 39
    assert summary["phase_count"] == 4
    assert summary["role_with_value_context_count"] == 39
    assert summary["role_with_freshness_context_count"] == 39
    assert summary["role_with_release_timing_context_count"] == 39
    assert summary["role_with_continuity_status_count"] == 39
    assert summary["stale_or_missing_explanation_count"] == 39


def test_phase60_continuity_preserves_missing_and_proxy_boundaries() -> None:
    artifact = build_evidence_freshness_release_value_continuity()

    assert artifact["current_numeric_value_available_count"] == 0
    assert artifact["metadata_ready_value_missing_count"] == 31
    assert artifact["authorized_input_required_count"] == 2
    assert artifact["supporting_proxy_only_count"] == 3
    assert artifact["source_metadata_incomplete_count"] == 3
    assert artifact["missing_value_treated_as_neutral_count"] == 0
    assert artifact["metadata_only_promoted_to_phase_support_count"] == 0
    assert artifact["supporting_proxy_replacement_allowed_count"] == 0


def test_phase60_continuity_links_transition_context_without_phase_emission() -> None:
    artifact = build_evidence_freshness_release_value_continuity()

    assert artifact["transition_continuity_context_count"] == 4
    assert artifact["transition_lane_context_count"] == 13
    assert artifact["phase59_declared_start_governance_deferred"] is True
    assert artifact["declared_phase_age_false_precision_count"] == 0
    assert artifact["standalone_classifier_added_count"] == 0
    assert artifact["phase_rank_or_score_added_count"] == 0
    assert artifact["current_data_used_to_infer_declared_phase_count"] == 0
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False
    assert artifact["production_behavior_change_count"] == 0


def test_phase60_view_model_is_research_only() -> None:
    view_model = build_evidence_freshness_release_value_continuity_view_model()

    assert view_model["view_id"] == "evidence_freshness_release_value_continuity"
    assert (
        view_model["output_mode"]
        == "research_only_evidence_freshness_release_value_continuity"
    )
    assert view_model["research_only"] is True
    assert view_model["continuity_card_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0
