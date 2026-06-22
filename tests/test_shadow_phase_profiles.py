from __future__ import annotations

from business_cycle.shadow_model.runner import run_shadow_evidence_model


def test_shadow_phase_profiles_do_not_compute_candidate_phase() -> None:
    result = run_shadow_evidence_model(as_of="2019-12-31", data_mode="vintage_as_of")

    assert result["formal_candidate_phase_computed"] is False
    assert result["phase_profile_count"] == 4
    assert all(
        profile["formal_candidate_phase_computed"] is False
        for profile in result["phase_profiles"]
    )
    assert any(
        profile["shadow_profile_status"] == "partial_evidence_profile"
        for profile in result["phase_profiles"]
    )

