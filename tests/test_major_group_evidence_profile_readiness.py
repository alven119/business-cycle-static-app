from __future__ import annotations

from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness,
    build_major_group_evidence_profile_readiness_view_model,
    summarize_major_group_evidence_profile_readiness,
)


def test_phase61_major_group_profile_artifact_passes() -> None:
    summary = summarize_major_group_evidence_profile_readiness()

    assert summary["result"] == "passed"
    assert summary["major_group_evidence_profile_readiness_ready"] is True
    assert summary["major_group_profile_count"] == 24
    assert summary["phase_count"] == 4
    assert summary["phase_with_major_group_profile_count"] == 4
    assert summary["profiled_role_count"] == 39
    assert summary["profiled_required_core_role_count"] == 37
    assert summary["profiled_supporting_role_count"] == 2
    assert summary["methodology_requirement_excluded_count"] == 1
    assert summary["missing_non_methodology_role_count"] == 0


def test_phase61_group_profiles_preserve_gap_boundaries() -> None:
    artifact = build_major_group_evidence_profile_readiness()

    assert artifact["required_core_group_profile_complete_count"] == 22
    assert artifact["supporting_only_group_count"] == 2
    assert artifact["core_metadata_ready_value_missing_group_count"] == 16
    assert artifact["core_authorized_input_required_group_count"] == 2
    assert artifact["core_supporting_proxy_visible_not_book_core_group_count"] == 1
    assert artifact["core_source_metadata_incomplete_abstain_group_count"] == 3
    assert artifact["supporting_proxy_context_group_count"] == 3
    assert artifact["group_ready_for_formal_phase_count"] == 0
    assert artifact["group_with_current_numeric_value_count"] == 0
    assert artifact["major_group_promoted_with_missing_core_count"] == 0
    assert artifact["supporting_proxy_replacement_allowed_count"] == 0
    assert artifact["missing_value_treated_as_neutral_count"] == 0
    assert artifact["metadata_only_promoted_to_phase_support_count"] == 0


def test_phase61_profiles_keep_methodology_and_supporting_roles_separate() -> None:
    artifact = build_major_group_evidence_profile_readiness()
    profiles = artifact["major_group_profiles"]
    trade = next(
        profile
        for profile in profiles
        if profile["phase_or_layer"] == "recovery"
        and profile["major_group_id"] == "trade"
    )
    policy_support = next(
        profile
        for profile in profiles
        if profile["major_group_id"] == "policy_financial_supporting_only"
    )

    assert trade["excluded_methodology_role_ids"] == [
        "recovery_publication_lag_awareness",
    ]
    assert trade["missing_non_methodology_role_ids"] == []
    assert policy_support["readiness_status"] == "supporting_only_not_phase_presence"
    assert policy_support["required_core_role_count"] == 0
    assert policy_support["group_ready_for_formal_phase"] is False


def test_phase61_view_model_is_research_only() -> None:
    view_model = build_major_group_evidence_profile_readiness_view_model()

    assert view_model["view_id"] == "major_group_evidence_profile_readiness"
    assert (
        view_model["output_mode"]
        == "research_only_major_group_evidence_profile_readiness"
    )
    assert view_model["research_only"] is True
    assert view_model["major_group_profile_count"] == 24
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0
    assert view_model["role_count_voting_added_count"] == 0
