from __future__ import annotations

from business_cycle.audits.macro_indicator_coverage_readiness_matrix import (
    build_macro_indicator_coverage_dashboard_view_model,
    build_macro_indicator_coverage_readiness_rows,
    summarize_macro_indicator_coverage_readiness_matrix,
)


def test_macro_indicator_coverage_readiness_matrix_passes() -> None:
    summary = summarize_macro_indicator_coverage_readiness_matrix()

    assert summary["result"] == "passed"
    assert summary["macro_indicator_coverage_readiness_matrix_ready"] is True
    assert summary["coverage_role_count"] == 39
    assert summary["phase_count"] == 4
    assert summary["phase_with_coverage_count"] == 4
    assert summary["role_with_source_tier_count"] == 39
    assert summary["role_with_data_risk_label_count"] == 39
    assert summary["role_with_dashboard_explanation_count"] == 39
    assert summary["role_with_next_gap_count"] == 39
    assert summary["dashboard_gap_burn_down_view_ready"] is True
    assert summary["supporting_proxy_only_count"] == 3
    assert summary["user_authorized_input_required_count"] == 2
    assert summary["false_resolution_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["proxy_promoted_to_book_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_macro_indicator_coverage_rows_make_all_phase_gaps_visible() -> None:
    rows = build_macro_indicator_coverage_readiness_rows()
    phases = {row["phase_or_layer"] for row in rows}

    assert phases == {"recovery", "growth", "boom", "recession"}
    assert all(row["coverage_status"] for row in rows)
    assert all(row["dashboard_display_status"] for row in rows)
    assert all(row["dashboard_explanation_zh"] for row in rows)
    assert all(row["next_gap_zh"] for row in rows)


def test_macro_indicator_coverage_preserves_proxy_boundaries() -> None:
    rows = {row["role_id"]: row for row in build_macro_indicator_coverage_readiness_rows()}

    assert rows["growth_adp_employment"]["user_authorized_input_required"] is True
    assert rows["boom_consumer_confidence"]["user_authorized_input_required"] is True
    assert rows["growth_adp_employment"]["supporting_proxy_can_replace_book_core"] is False
    assert (
        rows["boom_consumer_confidence"]["supporting_proxy_can_replace_book_core"]
        is False
    )
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "supporting_proxy_only"
    ] is True
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "book_core_replacement_allowed"
    ] is False


def test_macro_indicator_coverage_dashboard_view_model_is_research_only() -> None:
    view_model = build_macro_indicator_coverage_dashboard_view_model()

    assert view_model["view_id"] == "macro_indicator_coverage_readiness"
    assert view_model["output_mode"] == "research_only_dashboard_gap_burn_down"
    assert view_model["research_only"] is True
    assert len(view_model["phase_cards"]) == 4
    assert len(view_model["role_cards"]) == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0
    assert view_model["standalone_classifier_added_count"] == 0
