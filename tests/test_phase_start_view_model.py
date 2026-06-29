from __future__ import annotations

from business_cycle.cycle_state.phase_start_research_assistant import (
    PROHIBITED_FIELDS,
)
from business_cycle.cycle_state.phase_start_view_model import (
    build_phase_start_research_view_model,
)


def test_phase_start_view_model_labels_research_and_declared_state() -> None:
    view_model = build_phase_start_research_view_model()

    assert view_model["research_only"] is True
    assert view_model["readiness_label"] == (
        "phase_start_research_ready_registry_unchanged"
    )
    assert view_model["declared_state_label"] == (
        "declared_state_not_inferred_current_phase"
    )
    assert view_model["declared_current_phase"] == "boom"
    assert view_model["legal_next_phase"] == "recession"
    assert view_model["registry_write_allowed"] is False
    assert view_model["trust_metadata"]["uses_current_data_to_infer_declared_phase"] is False


def test_phase_start_view_model_has_no_prohibited_fields() -> None:
    view_model = build_phase_start_research_view_model()

    assert PROHIBITED_FIELDS.isdisjoint(view_model)
    assert "declared_registry_auto_write" in view_model["prohibited_uses"]
    assert "portfolio_action" in view_model["prohibited_uses"]


def test_phase_start_view_model_exposes_hypothesis_and_phase48_context() -> None:
    view_model = build_phase_start_research_view_model()

    hypothesis_ids = {
        item["hypothesis_id"]
        for item in view_model["hypothesis_summaries"]
    }
    assert "user_prior_hypothesis" in hypothesis_ids
    assert "evidence_based_research_hypothesis" in hypothesis_ids
    assert view_model["top_phase48_evidence_wiring_priorities"]
    assert view_model["missing_evidence_summary"]["missing_evidence_count"] >= 0
