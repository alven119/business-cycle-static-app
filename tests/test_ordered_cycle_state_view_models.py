from __future__ import annotations

from business_cycle.cycle_state.declared_phase_registry import load_declared_cycle_state
from business_cycle.cycle_state.view_models import (
    FORBIDDEN_VIEW_FIELDS,
    build_declared_cycle_state_view_model,
)


def test_view_model_labels_declared_state_not_inferred_phase() -> None:
    view_model = build_declared_cycle_state_view_model(load_declared_cycle_state())
    payload = view_model.to_dict()

    assert payload["declared_state_label"] == "declared_state_not_inferred_current_phase"
    assert payload["declared_current_phase"] == "boom"
    assert payload["legal_previous_phase"] == "growth"
    assert payload["legal_next_phase"] == "recession"
    assert payload["formal_current_phase_inference_enabled"] is False
    assert payload["trust_metadata"]["uses_current_data_to_infer_phase"] is False
    assert payload["trust_metadata"]["production_behavior_change"] is False


def test_view_model_has_no_forbidden_decision_or_action_fields() -> None:
    payload = build_declared_cycle_state_view_model(load_declared_cycle_state()).to_dict()

    assert FORBIDDEN_VIEW_FIELDS.isdisjoint(payload)
    assert "formal_current_phase_inference" in payload["prohibited_uses"]
    assert "phase_score_or_rank_selection" in payload["prohibited_uses"]
    assert "portfolio_action" in payload["prohibited_uses"]


def test_view_model_carries_deferred_capability_gaps() -> None:
    payload = build_declared_cycle_state_view_model(load_declared_cycle_state()).to_dict()

    assert "user_declared_phase_start_date_required_for_precise_age" in payload[
        "deferred_capability_gaps"
    ]
    assert "transition_monitor_not_implemented_in_phase45" in payload[
        "deferred_capability_gaps"
    ]
