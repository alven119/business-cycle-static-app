from __future__ import annotations

from business_cycle.render.phase_evidence_view_models import (
    build_phase_analysis_view_model,
    build_transition_risk_view_model,
    summarize_phase_evidence_view_models,
)


def test_phase_evidence_view_models_have_trust_metadata_and_no_action_fields() -> None:
    summary = summarize_phase_evidence_view_models()

    assert summary["phase_evidence_view_model_ready"] is True
    assert summary["missing_trust_metadata_count"] == 0
    assert summary["observation_mislabeled_as_phase_evidence_count"] == 0
    assert summary["watch_mislabeled_as_confirmation_count"] == 0
    assert summary["research_mislabeled_as_production_count"] == 0
    assert summary["prohibited_action_field_count"] == 0


def test_phase_and_transition_view_models_are_research_only() -> None:
    phase = build_phase_analysis_view_model()
    transition = build_transition_risk_view_model()

    assert phase["readiness_label"] == "shadow_research_only_candidate_disabled"
    assert transition["readiness_label"] == "shadow_research_only_candidate_disabled"
    assert "portfolio_action" in phase["prohibited_uses"]
    assert "candidate_phase_selection" in transition["prohibited_uses"]
