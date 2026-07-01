from __future__ import annotations

from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
    build_indicator_detail_source_risk_value_view_model,
    summarize_indicator_detail_source_risk_value_rendering,
)


def test_indicator_detail_source_risk_value_rendering_passes() -> None:
    summary = summarize_indicator_detail_source_risk_value_rendering()

    assert summary["result"] == "passed"
    assert summary["indicator_detail_source_risk_value_rendering_ready"] is True
    assert summary["indicator_detail_card_count"] == 39
    assert summary["phase_count"] == 4
    assert summary["source_risk_visible_card_count"] == 39
    assert summary["freshness_context_visible_card_count"] == 39
    assert summary["release_timing_context_visible_card_count"] == 39
    assert summary["value_context_visible_card_count"] == 39
    assert summary["transformation_context_visible_card_count"] == 39
    assert summary["why_not_evidence_visible_card_count"] == 39
    assert summary["authorized_input_missing_card_count"] == 2
    assert summary["supporting_proxy_only_card_count"] == 3
    assert summary["proxy_promoted_to_book_core_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_indicator_detail_cards_preserve_proxy_and_authorized_input_boundaries() -> None:
    cards = {
        card["role_id"]: card for card in build_indicator_detail_source_risk_value_cards()
    }

    adp = cards["growth_adp_employment"]
    confidence = cards["boom_consumer_confidence"]
    trough_policy = cards["trough_policy_financial_not_sufficient_alone"]

    assert adp["user_authorized_input_required"] is True
    assert adp["value_context_status"] == (
        "authorized_private_or_user_input_required_no_numeric_value"
    )
    assert confidence["user_authorized_input_required"] is True
    assert trough_policy["supporting_proxy_only"] is True
    assert trough_policy["book_core_replacement_allowed"] is False
    assert trough_policy["supporting_proxy_can_replace_book_core"] is False
    assert "supporting-only" in trough_policy["why_not_evidence_zh"]
    assert "cannot confirm" in trough_policy["why_not_evidence_zh"]


def test_indicator_detail_cards_show_value_context_without_phase_support() -> None:
    cards = {
        card["role_id"]: card for card in build_indicator_detail_source_risk_value_cards()
    }
    claims = cards["boom_claims_u_shape"]
    growth_income = cards["growth_real_disposable_income_vs_consumption"]

    assert claims["value_context_visible"] is True
    assert claims["latest_observation_context"]
    assert claims["phase_support_added"] is False
    assert growth_income["transformation_semantics_status"] == (
        "same_as_of_real_relation_visible_phase_support_not_operational"
    )
    assert growth_income["phase_support_added"] is False
    assert growth_income["candidate_selection_eligible"] is False


def test_indicator_detail_view_model_is_research_only() -> None:
    view_model = build_indicator_detail_source_risk_value_view_model()

    assert view_model["view_id"] == "indicator_detail_source_risk_value_cards"
    assert view_model["output_mode"] == "research_only_indicator_detail_context"
    assert view_model["research_only"] is True
    assert view_model["card_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0
    assert view_model["standalone_classifier_added_count"] == 0
