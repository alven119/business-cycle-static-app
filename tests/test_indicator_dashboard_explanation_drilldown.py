from __future__ import annotations

from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown,
    build_indicator_dashboard_explanation_drilldown_view_model,
    summarize_indicator_dashboard_explanation_drilldown,
)


def test_phase62_indicator_dashboard_drilldown_passes() -> None:
    summary = summarize_indicator_dashboard_explanation_drilldown()

    assert summary["result"] == "passed"
    assert summary["indicator_dashboard_explanation_drilldown_ready"] is True
    assert summary["major_group_drilldown_count"] == 24
    assert summary["role_drilldown_count"] == 39
    assert summary["role_with_source_detail_count"] == 39
    assert summary["role_with_release_timing_detail_count"] == 39
    assert summary["role_with_freshness_detail_count"] == 39
    assert summary["role_with_transformation_detail_count"] == 39
    assert summary["role_with_rule_or_usability_detail_count"] == 39
    assert summary["role_with_provenance_detail_count"] == 39
    assert summary["role_with_abstention_reason_count"] == 39
    assert summary["role_with_diagnostic_transparency_count"] == 39
    assert summary["role_with_chart_payload_count"] == 39
    assert summary["role_with_ytd_chart_payload_count"] == 39
    assert summary["role_with_trailing_1y_chart_payload_count"] == 39
    assert summary["role_with_trailing_5y_chart_payload_count"] == 39
    assert summary["source_rule_provenance_complete"] is True


def test_phase62_drilldown_links_groups_to_roles_without_selection() -> None:
    artifact = build_indicator_dashboard_explanation_drilldown()

    role_ids = {role["role_id"] for role in artifact["role_drilldowns"]}
    linked_role_ids = {
        link["role_id"]
        for group in artifact["major_group_drilldowns"]
        for link in group["role_links"]
    }

    assert linked_role_ids == role_ids
    assert artifact["group_ready_for_formal_phase_count"] == 0
    assert artifact["standalone_classifier_added_count"] == 0
    assert artifact["phase_rank_or_score_added_count"] == 0
    assert artifact["role_count_voting_added_count"] == 0
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False


def test_phase62_role_drilldowns_preserve_abstention_and_source_risk() -> None:
    artifact = build_indicator_dashboard_explanation_drilldown()

    for role in artifact["role_drilldowns"]:
        assert role["source_detail"]["source_family"]
        assert role["release_timing_detail"]["series_release_rows"]
        assert role["freshness_detail"]["freshness_context_status"]
        assert role["transformation_detail"]["transformation_semantics_status"]
        assert role["rule_or_usability_detail"]["evidence_usability_status"]
        assert role["provenance_detail"]["research_only"] is True
        assert role["data_mode_detail"]["point_in_time_result"] is False
        assert role["abstention_reason_detail"]["why_not_evidence_zh"]
        assert role["abstention_reason_detail"]["stale_or_missing_explanation_zh"]
        assert role["diagnostic_transparency_detail"]["method_recipe_visible"] is True
        assert (
            role["diagnostic_transparency_detail"]["computed_diagnostic_value_present"]
            is False
        )
        assert role["chart_payload_detail"]["chart_data_mode"] == "local_cache_or_unavailable"
        assert set(role["chart_payload_detail"]["allowed_periods"]) == {
            "ytd",
            "trailing_1y",
            "trailing_5y",
        }
        assert role["missing_value_treated_as_neutral"] is False
        assert role["metadata_only_promoted_to_phase_support"] is False
        assert role["supporting_proxy_replacement_allowed"] is False


def test_phase62_view_model_is_research_only() -> None:
    view_model = build_indicator_dashboard_explanation_drilldown_view_model()

    assert view_model["view_id"] == "indicator_dashboard_explanation_drilldown"
    assert view_model["research_only"] is True
    assert view_model["role_drilldown_count"] == 39
    assert view_model["role_with_diagnostic_transparency_count"] == 39
    assert view_model["role_with_chart_payload_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0
