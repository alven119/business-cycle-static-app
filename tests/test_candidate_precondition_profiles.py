from __future__ import annotations

from business_cycle.shadow_model.candidate_precondition_profiles import (
    build_candidate_precondition_profiles,
    summarize_candidate_precondition_profiles,
)


def test_candidate_precondition_profiles_are_diagnostics_only() -> None:
    summary = summarize_candidate_precondition_profiles()

    assert summary["candidate_precondition_profile_ready"] is True
    assert summary["candidate_input_eligibility_rule_count"] > 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["candidate_output_field_count"] == 0
    assert summary["candidate_input_eligible_profile_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0


def test_candidate_precondition_profiles_do_not_emit_phase_fields() -> None:
    profiles = build_candidate_precondition_profiles()

    assert {row["profile_id"] for row in profiles} == {
        "recovery_precondition",
        "growth_precondition",
        "boom_precondition",
        "recession_confirmation_precondition",
    }
    forbidden_keys = {"candidate_phase", "selected_candidate_phase", "current_phase"}
    assert all(forbidden_keys.isdisjoint(row) for row in profiles)
    assert all(row["candidate_input_eligible"] is False for row in profiles)
    assert all(row["candidate_phase_emitted"] is False for row in profiles)
    assert all(row["current_phase_emitted"] is False for row in profiles)
    assert all(
        "candidate_output_disabled_by_phase13_contract"
        in row["readiness_blockers"]
        for row in profiles
    )
