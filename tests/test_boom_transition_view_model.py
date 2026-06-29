from __future__ import annotations

from business_cycle.transition_monitor.boom_transition_monitor import PROHIBITED_FIELDS
from business_cycle.transition_monitor.boom_transition_view_model import (
    build_boom_transition_view_model,
)


def test_boom_transition_view_model_labels_declared_state_and_research_only() -> None:
    view_model = build_boom_transition_view_model()

    assert view_model["declared_state_label"] == "declared_state_not_inferred_current_phase"
    assert view_model["legal_transition_label"] == "boom_to_recession"
    assert view_model["watch_confirmation_label"] == "watch_not_confirmation"
    assert view_model["research_only"] is True
    assert view_model["declared_current_phase"] == "boom"
    assert view_model["legal_next_phase"] == "recession"
    assert view_model["trust_metadata"]["uses_current_data_to_infer_declared_phase"] is False


def test_boom_transition_view_model_has_no_prohibited_fields() -> None:
    view_model = build_boom_transition_view_model()

    assert PROHIBITED_FIELDS.isdisjoint(view_model)
    assert "phase_score_or_rank_selection" in view_model["prohibited_uses"]
    assert "portfolio_action" in view_model["prohibited_uses"]


def test_boom_transition_view_model_lane_summaries_preserve_watch_confirmation_split() -> None:
    lanes = build_boom_transition_view_model()["lane_summaries"]

    assert lanes["boom_ending_watch"]["watch_lane"] is True
    assert lanes["recession_watch"]["watch_lane"] is True
    assert lanes["recession_confirmation"]["confirmation_lane"] is True
    assert lanes["recession_confirmation"]["watch_lane"] is False
