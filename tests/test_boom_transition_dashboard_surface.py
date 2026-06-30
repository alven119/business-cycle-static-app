from __future__ import annotations

from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
    summarize_boom_transition_dashboard_surface,
)


def test_boom_transition_dashboard_surface_has_indicator_meanings_and_status() -> None:
    surface = build_boom_transition_dashboard_surface()

    assert surface["result"] == "passed"
    assert surface["declared_current_phase"] == "boom"
    assert surface["legal_next_phase"] == "recession"
    assert len(surface["lane_cards"]) == 4
    assert len(surface["indicator_cards"]) == 5
    assert {card["role_id"] for card in surface["indicator_cards"]} == {
        "boom_claims_u_shape",
        "boom_retail_sales_vs_broad_pce",
        "boom_private_investment",
        "recession_employment_confirmation",
        "recession_consumption_confirmation",
    }
    assert all(card["meaning_zh"] for card in surface["indicator_cards"])
    assert all(card["status_label_zh"] for card in surface["indicator_cards"])
    assert all(
        card["abstention_or_blocker_reason_zh"]
        for card in surface["indicator_cards"]
    )


def test_boom_transition_dashboard_surface_preserves_doctrine_boundaries() -> None:
    summary = summarize_boom_transition_dashboard_surface()

    assert summary["boom_transition_dashboard_surface_ready"] is True
    assert summary["watch_confirmation_separation_visible"] is True
    assert summary["prohibited_surface_field_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
