from __future__ import annotations

from business_cycle.audits.phase64_indicator_transparency_chart_payload_closure import (
    summarize_phase64_indicator_transparency_chart_payload_closure,
)


def test_phase64_indicator_transparency_chart_payload_closure_passes() -> None:
    summary = summarize_phase64_indicator_transparency_chart_payload_closure()

    assert summary["result"] == "passed"
    assert summary["phase64_indicator_transparency_chart_payload_ready"] is True
    assert summary["indicator_chart_explanation_payload_ready"] is True
    assert summary["latest_evidence_dashboard_page_ready"] is True
    assert summary["role_payload_count"] == 39
    assert summary["role_with_diagnostic_transparency_count"] == 39
    assert summary["role_with_chart_payload_count"] == 39
    assert summary["rendered_score_transparency_count"] == 39
    assert summary["rendered_chart_payload_count"] == 39
    assert summary["rendered_ytd_chart_period_count"] == 39
    assert summary["rendered_trailing_1y_chart_period_count"] == 39
    assert summary["rendered_trailing_5y_chart_period_count"] == 39
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert (
        summary["phase64_closure_status"]
        == "closed_indicator_transparency_chart_payload_ready_no_phase_selection"
    )


def test_phase64_product_doctrine_alignment_counts() -> None:
    summary = summarize_phase64_indicator_transparency_chart_payload_closure()

    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["diagnostic_score_product_answer_count"] == 0
    assert summary["unavailable_chart_treated_as_zero_count"] == 0
    assert summary["missing_value_treated_as_neutral_count"] == 0
    assert summary["product_doctrine_alignment_status"] == "aligned"
