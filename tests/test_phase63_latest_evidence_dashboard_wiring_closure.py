from __future__ import annotations

from business_cycle.audits.phase63_latest_evidence_dashboard_wiring_closure import (
    summarize_phase63_latest_evidence_dashboard_wiring_closure,
)


def test_phase63_latest_evidence_dashboard_wiring_closure_passes() -> None:
    summary = summarize_phase63_latest_evidence_dashboard_wiring_closure()

    assert summary["result"] == "passed"
    assert summary["phase63_latest_evidence_dashboard_wiring_ready"] is True
    assert summary["latest_evidence_dashboard_page_ready"] is True
    assert summary["dashboard_indicator_drilldown_view_ready"] is True
    assert summary["dashboard_bundle_latest_evidence_ready"] is True
    assert summary["rendered_latest_evidence_page_count"] == 1
    assert summary["major_group_drilldown_rendered_count"] == 24
    assert summary["role_drilldown_rendered_count"] == 39
    assert summary["role_source_detail_rendered_count"] == 39
    assert summary["role_release_timing_detail_rendered_count"] == 39
    assert summary["role_freshness_detail_rendered_count"] == 39
    assert summary["role_transformation_detail_rendered_count"] == 39
    assert summary["role_rule_usability_detail_rendered_count"] == 39
    assert summary["role_provenance_detail_rendered_count"] == 39
    assert summary["role_abstention_detail_rendered_count"] == 39
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase63_product_doctrine_alignment_counts() -> None:
    summary = summarize_phase63_latest_evidence_dashboard_wiring_closure()

    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["cycle_state_machine_alignment_status"]
        == "latest_evidence_dashboard_wired_declared_state_preserved"
    )
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_capability_progress_impacted_count"] == 5
