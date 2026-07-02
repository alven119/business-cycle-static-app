from __future__ import annotations

from business_cycle.audits.phase62_indicator_dashboard_explanation_drilldown_closure import (
    summarize_phase62_indicator_dashboard_explanation_drilldown_closure,
)


def test_phase62_indicator_dashboard_explanation_drilldown_closure_passes() -> None:
    summary = summarize_phase62_indicator_dashboard_explanation_drilldown_closure()

    assert summary["result"] == "passed"
    assert summary["phase62_indicator_dashboard_explanation_drilldown_ready"] is True
    assert summary["indicator_dashboard_explanation_drilldown_ready"] is True
    assert summary["dashboard_indicator_drilldown_view_ready"] is True
    assert summary["product_capability_progress_ready"] is True
    assert summary["role_drilldown_count"] == 39
    assert summary["major_group_drilldown_count"] == 24
    assert summary["source_rule_provenance_complete"] is True
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert (
        summary["phase62_closure_status"]
        == "closed_indicator_dashboard_explanation_drilldown_ready_no_phase_emission"
    )


def test_phase62_closure_advances_explainability_without_production_change() -> None:
    summary = summarize_phase62_indicator_dashboard_explanation_drilldown_closure()

    assert "C3_EXPLAINABILITY_AND_ATTRIBUTION" in summary[
        "product_capabilities_advanced"
    ]
    assert "W4_INDICATOR_EXPLORER" in summary["web_surfaces_advanced"]
    assert "W7_DATA_LINEAGE" in summary["web_surfaces_advanced"]
    assert summary["production_behavior_change_count"] == 0
    assert summary["legacy_v1_behavior_modified_count"] == 0
    assert summary["portfolio_policy_output_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["semantic_drift_count"] == 0
