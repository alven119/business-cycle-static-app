from __future__ import annotations

from business_cycle.audits.phase54_low_cost_macro_source_completion_closure import (
    summarize_phase54_low_cost_macro_source_completion_closure,
)


def test_phase54_low_cost_macro_source_completion_closure_passes() -> None:
    summarize_phase54_low_cost_macro_source_completion_closure.cache_clear()
    summary = summarize_phase54_low_cost_macro_source_completion_closure()

    assert summary["result"] == "passed"
    assert summary["phase54_low_cost_macro_source_completion_ready"] is True
    assert summary["low_cost_macro_source_completion_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["remaining_phase54_role_count"] == 2
    assert summary["low_cost_path_defined_role_count"] == 2
    assert summary["macromicro_api_candidate_count"] == 0
    assert summary["unaffordable_paid_api_candidate_count"] == 0
    assert summary["book_core_replacement_without_license_count"] == 0
    assert summary["payems_replaces_adp_count"] == 0
    assert summary["generic_sentiment_replaces_consumer_confidence_count"] == 0
    assert summary["proxy_promoted_to_book_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_impacted_count"] == 5
    assert summary["next_recommended_phase"] == (
        "Phase55_indicator_detail_low_cost_source_risk_wiring"
    )
    assert summary["phase54_closure_status"] == (
        "closed_low_cost_macro_source_completion_ready_no_paid_api_or_phase_emission"
    )
