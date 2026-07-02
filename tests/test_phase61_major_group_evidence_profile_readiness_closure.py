from __future__ import annotations

from business_cycle.audits.phase61_major_group_evidence_profile_readiness_closure import (
    summarize_phase61_major_group_evidence_profile_readiness_closure,
)


def test_phase61_major_group_evidence_profile_readiness_closure_passes() -> None:
    summary = summarize_phase61_major_group_evidence_profile_readiness_closure()

    assert summary["result"] == "passed"
    assert summary["phase61_major_group_evidence_profile_readiness_ready"] is True
    assert summary["major_group_evidence_profile_readiness_ready"] is True
    assert summary["dashboard_major_group_profile_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["major_group_profile_count"] == 24
    assert summary["profiled_role_count"] == 39
    assert summary["methodology_requirement_excluded_count"] == 1
    assert summary["missing_non_methodology_role_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert (
        summary["phase61_closure_status"]
        == "closed_major_group_evidence_profiles_ready_no_phase_emission"
    )


def test_phase61_closure_keeps_group_profiles_explanation_only() -> None:
    summary = summarize_phase61_major_group_evidence_profile_readiness_closure()

    assert summary["group_ready_for_formal_phase_count"] == 0
    assert summary["major_group_promoted_with_missing_core_count"] == 0
    assert summary["supporting_proxy_replacement_allowed_count"] == 0
    assert summary["missing_value_treated_as_neutral_count"] == 0
    assert summary["metadata_only_promoted_to_phase_support_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert (
        summary["next_recommended_phase"]
        == "Phase62_indicator_to_dashboard_explanation_drill_down"
    )
