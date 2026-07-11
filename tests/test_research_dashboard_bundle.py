from __future__ import annotations

from functools import lru_cache

import pytest

import business_cycle.render.research_dashboard_bundle as dashboard_bundle_module
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    summarize_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)
from business_cycle.audits.macro_indicator_coverage_readiness_matrix import (
    build_macro_indicator_coverage_dashboard_view_model,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_view_model,
)
from business_cycle.render.boom_to_recession_transition_surface import (
    build_boom_to_recession_transition_surface_view_model,
)
from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_template_view_model,
)
from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity_view_model,
)
from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness_view_model,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
)
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    build_local_current_cache_dashboard_bridge_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)
from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation_view_model,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
)
from business_cycle.render.nas_portfolio_replay_lab import (
    build_nas_portfolio_replay_lab,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
)
from business_cycle.audits.phase125_strict_replay_backtest_closure import (
    build_phase125_fixture_timeline,
    summarize_phase125_strict_replay_backtest_closure,
)
from business_cycle.audits.phase126_nas_v1_operational_acceptance_closure import (
    summarize_phase126_nas_v1_operational_acceptance_closure,
)
from business_cycle.render.nas_service_dashboard import (
    render_historical_replay_page,
    render_portfolio_research_page,
)


@pytest.fixture(scope="module", autouse=True)
def cache_dashboard_base_dependencies() -> None:
    """Keep every assertion while avoiding repeated immutable governance builds."""

    patcher = pytest.MonkeyPatch()
    for name in (
        "build_post_pit_remediation_validation_rerun",
        "summarize_recession_recovery_pit_gap_matrix",
        "summarize_qa12_major_group_manual_start_closure",
    ):
        original = getattr(dashboard_bundle_module, name)
        patcher.setattr(dashboard_bundle_module, name, lru_cache(maxsize=1)(original))
    yield
    patcher.undo()


def test_research_dashboard_bundle_reconciles_authoritative_counts() -> None:
    summary = summarize_research_dashboard_bundle()

    assert summary["research_dashboard_contract_ready"] is True
    assert summary["research_dashboard_bundle_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["comparable_scenario_count"] == 2
    assert summary["non_comparable_scenario_count"] == 3
    assert summary["comparable_scenario_ids"] == [
        "euro_debt_slowdown_2011_2012",
        "late_cycle_2018_2019",
    ]
    assert summary["non_comparable_scenario_ids"] == [
        "dotcom_cycle_2000_2003",
        "global_financial_crisis_2007_2009",
        "covid_recession_2020",
    ]
    assert summary["remaining_pit_role_gap_count"] == 6
    assert summary["rule_unresolved_gap_count"] == 1
    assert summary["historical_accuracy_metric_registry_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["artifact_consistency_error_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["label_used_by_runtime_count"] == 0


def test_phase124_nas_portfolio_and_replay_surfaces_are_operational_without_execution() -> None:
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    snapshot["source_release_diagnostics"] = {
        "strict_replay_input_timeline": {
            "complete_month_count": 0,
            "abstention_month_count": 156,
            "timeline_rows": [],
        }
    }
    live = build_live_ordered_cycle_evidence(snapshot)

    lab = build_nas_portfolio_replay_lab(
        snapshot,
        live_transition_evidence=live,
    )

    assert lab["result"] == "passed"
    assert lab["policy_template_count"] == 8
    assert lab["scenario_count"] == 5
    assert lab["monthly_playhead_row_count"] == 156
    assert lab["replay_data_mode_count"] == 2
    assert lab["portfolio_research_route_operational"] is True
    assert lab["historical_event_replay_route_operational"] is True
    assert lab["strict_revised_fallback_count"] == 0
    assert lab["current_allocation_recommendation_count"] == 0
    assert lab["model_execution_count"] == 0
    assert lab["backtest_execution_count"] == 0
    assert lab["candidate_phase_emitted"] is False
    assert lab["current_phase_emitted"] is False


def test_phase125_strict_replay_and_backtest_results_reach_existing_nas_surfaces() -> None:
    summary = summarize_phase125_strict_replay_backtest_closure()
    artifact = summary["artifact"]
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    snapshot["source_release_diagnostics"] = {
        "strict_replay_input_timeline": build_phase125_fixture_timeline(),
        "strict_replay_backtest_status": artifact,
    }
    live = build_live_ordered_cycle_evidence(snapshot)
    lab = build_nas_portfolio_replay_lab(snapshot, live_transition_evidence=live)
    navigation = [
        {"nav_id": "portfolio_research", "label_zh": "配置研究", "path": "/portfolio-research", "enabled": True},
        {"nav_id": "historical_replay", "label_zh": "歷史重播", "path": "/historical-replay", "enabled": True},
    ]
    portfolio_html = render_portfolio_research_page(
        lab["portfolio_research"], navigation=navigation
    )
    replay_html = render_historical_replay_page(
        lab["historical_replay"], navigation=navigation
    )

    assert summary["result"] == "passed"
    assert artifact["strict_replay_complete_scenario_count"] == 2
    assert artifact["strict_replay_blocked_scenario_count"] == 3
    assert artifact["evidence_replay_output_count"] == 48
    assert artifact["research_backtest_result_count"] == 16
    assert artifact["unitized_nav_result_count"] == 16
    assert artifact["xirr_result_count"] == 16
    assert artifact["book_benchmark_result_count"] == 0
    assert lab["phase125_execution_connected"] is True
    assert lab["phase125_research_backtest_result_count"] == 16
    assert "16 組" in portfolio_html
    assert "年化 TWR" in portfolio_html
    assert "Strict evidence" in replay_html
    assert "固定參數 sensitivity" in replay_html
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False


def test_phase126_private_nas_v1_operational_acceptance_is_complete_but_not_economic_validation() -> None:
    summary = summarize_phase126_nas_v1_operational_acceptance_closure()
    artifact = summary["artifact"]

    assert summary["result"] == "passed"
    assert artifact["strict_replay_rerun_verified"] is True
    assert artifact["retained_snapshot_count"] == 2
    assert artifact["retained_snapshot_checksum_valid"] is True
    assert artifact["backup_restore_drill_passed"] is True
    assert artifact["rollback_drill_passed"] is True
    assert artifact["mobile_current_routes_verified"] is True
    assert artifact["nas_v1_operational_acceptance_passed"] is True
    assert artifact["formal_production_validated"] is False
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False


def test_research_dashboard_bundle_is_research_only_and_trusted() -> None:
    bundle = build_research_dashboard_bundle()
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert validation["missing_trust_metadata_count"] == 0
    assert validation["prohibited_action_field_count"] == 0
    assert bundle["output_mode"] == "research_only"
    assert bundle["trust_metadata"]["output_label"] == "research_only"
    assert "production_decision" in bundle["prohibited_uses"]
    assert bundle["safety_counters"]["economic_performance_metric_count"] == 0


def test_research_dashboard_bundle_accepts_macro_coverage_view_model() -> None:
    macro_coverage = build_macro_indicator_coverage_dashboard_view_model()
    bundle = build_research_dashboard_bundle(macro_coverage_matrix=macro_coverage)
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "macro_indicator_coverage_readiness" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["macro_indicator_coverage_readiness"]["research_only"] is True
    assert (
        bundle["macro_indicator_coverage_readiness"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["macro_indicator_coverage_readiness"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_indicator_detail_view_model() -> None:
    indicator_detail = build_indicator_detail_source_risk_value_view_model()
    bundle = build_research_dashboard_bundle(indicator_detail_cards=indicator_detail)
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "indicator_detail_source_risk_value_cards" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["indicator_detail_source_risk_value_cards"]["research_only"] is True
    assert (
        bundle["indicator_detail_source_risk_value_cards"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["indicator_detail_source_risk_value_cards"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_boom_to_recession_completion_view_model() -> None:
    transition_surface = build_boom_to_recession_transition_surface_view_model()
    bundle = build_research_dashboard_bundle(
        boom_to_recession_transition_surface=transition_surface,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "boom_to_recession_transition_surface_completion" in {
        view["view_id"] for view in bundle["views"]
    }
    assert (
        bundle["boom_to_recession_transition_surface_completion"]["research_only"]
        is True
    )
    assert (
        bundle["boom_to_recession_transition_surface_completion"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["boom_to_recession_transition_surface_completion"][
            "current_phase_emitted"
        ]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_ordered_cycle_transition_templates() -> None:
    transition_templates = build_full_ordered_cycle_transition_lane_template_view_model()
    bundle = build_research_dashboard_bundle(
        ordered_cycle_transition_lane_templates=transition_templates,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "full_ordered_cycle_transition_lane_templates" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["full_ordered_cycle_transition_lane_templates"]["research_only"] is True
    assert (
        bundle["full_ordered_cycle_transition_lane_templates"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["full_ordered_cycle_transition_lane_templates"][
            "current_phase_emitted"
        ]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_evidence_continuity_view_model() -> None:
    continuity = build_evidence_freshness_release_value_continuity_view_model()
    bundle = build_research_dashboard_bundle(
        evidence_freshness_release_value_continuity=continuity,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "evidence_freshness_release_value_continuity" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["evidence_freshness_release_value_continuity"]["research_only"] is True
    assert (
        bundle["evidence_freshness_release_value_continuity"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["evidence_freshness_release_value_continuity"][
            "current_phase_emitted"
        ]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_major_group_profile_view_model() -> None:
    major_group_profiles = build_major_group_evidence_profile_readiness_view_model()
    bundle = build_research_dashboard_bundle(
        major_group_evidence_profile_readiness=major_group_profiles,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "major_group_evidence_profile_readiness" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["major_group_evidence_profile_readiness"]["research_only"] is True
    assert (
        bundle["major_group_evidence_profile_readiness"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["major_group_evidence_profile_readiness"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_indicator_drilldown_view_model() -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "indicator_dashboard_explanation_drilldown" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["indicator_dashboard_explanation_drilldown"]["research_only"] is True
    assert (
        bundle["indicator_dashboard_explanation_drilldown"][
            "candidate_phase_emitted"
        ]
        is False
    )
    assert (
        bundle["indicator_dashboard_explanation_drilldown"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_portfolio_policy_replay_surface() -> None:
    replay_surface = build_portfolio_replay_dashboard_surface_view_model()
    policy_surface = build_portfolio_policy_replay_research_surface_view_model()
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=replay_surface,
        portfolio_policy_replay_research_surface=policy_surface,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "portfolio_policy_replay_research_surface" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["portfolio_policy_replay_research_surface"]["research_only"] is True
    assert (
        bundle["portfolio_policy_replay_research_surface"][
            "portfolio_policy_replay_research_surface_ready"
        ]
        is True
    )
    assert (
        bundle["portfolio_policy_replay_research_surface"][
            "scenario_policy_coverage_row_count"
        ]
        == 40
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_transition_timing_replay_preview() -> None:
    preview = build_transition_timing_replay_preview_view_model()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=preview,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "transition_timing_replay_preview" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["transition_timing_replay_preview"]["research_only"] is True
    assert bundle["transition_timing_replay_preview"]["candidate_phase_emitted"] is False
    assert bundle["transition_timing_replay_preview"]["current_phase_emitted"] is False
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_transition_risk_accumulation() -> None:
    preview = build_transition_timing_replay_preview_view_model()
    accumulation = build_transition_risk_evidence_accumulation_view_model(
        transition_timing_replay_preview=preview,
    )
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=preview,
        transition_risk_evidence_accumulation=accumulation,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "transition_risk_evidence_accumulation" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["transition_risk_evidence_accumulation"]["research_only"] is True
    assert (
        bundle["transition_risk_evidence_accumulation"][
            "transition_risk_evidence_accumulation_ready"
        ]
        is True
    )
    assert (
        bundle["transition_risk_evidence_accumulation"][
            "transition_accumulation_lane_card_count"
        ]
        == 13
    )
    assert (
        bundle["transition_risk_evidence_accumulation"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["transition_risk_evidence_accumulation"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_current_macro_numeric_chart_coverage() -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "current_macro_numeric_chart_coverage" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["current_macro_numeric_chart_coverage"]["research_only"] is True
    assert (
        bundle["current_macro_numeric_chart_coverage"][
            "role_with_numeric_context_count"
        ]
        == 37
    )
    assert (
        bundle["current_macro_numeric_chart_coverage"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["current_macro_numeric_chart_coverage"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_local_current_cache_bridge() -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_local_current_cache_dashboard_bridge_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert bundle["current_macro_numeric_chart_coverage"]["research_only"] is True
    assert bundle["current_macro_numeric_chart_coverage"]["data_mode"] == (
        "revised_tmp_seeded_local_current_cache_rehearsal"
    )
    assert (
        bundle["current_macro_numeric_chart_coverage"][
            "phase74_local_current_cache_bridge_ready"
        ]
        is True
    )
    assert (
        bundle["current_macro_numeric_chart_coverage"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["current_macro_numeric_chart_coverage"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_portfolio_replay_surface() -> None:
    surface = build_portfolio_replay_dashboard_surface_view_model()
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=surface,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "portfolio_replay_dashboard_surface" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["portfolio_replay_dashboard_surface"]["research_only"] is True
    assert (
        bundle["portfolio_replay_dashboard_surface"][
            "research_backtest_artifact_count"
        ]
        == 10
    )
    assert (
        len(bundle["portfolio_replay_dashboard_surface"]["dashboard_cards"])
        == 10
    )
    assert bundle["portfolio_replay_dashboard_surface"]["metric_value_count"] == 0
    assert (
        bundle["portfolio_replay_dashboard_surface"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["portfolio_replay_dashboard_surface"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_dashboard_decision_explanation() -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    explanation = build_dashboard_decision_explanation_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=explanation,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "dashboard_decision_explanation" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["dashboard_decision_explanation"]["research_only"] is True
    assert (
        bundle["dashboard_decision_explanation"][
            "dashboard_decision_explanation_ready"
        ]
        is True
    )
    assert bundle["dashboard_decision_explanation"]["declared_current_phase"] == "boom"
    assert bundle["dashboard_decision_explanation"]["legal_next_phase"] == "recession"
    assert bundle["dashboard_decision_explanation"]["narrative_card_count"] == 5
    assert bundle["dashboard_decision_explanation"]["candidate_phase_emitted"] is False
    assert bundle["dashboard_decision_explanation"]["current_phase_emitted"] is False
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_current_data_refresh_ux() -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    refresh_ux = build_current_data_refresh_ux_view_model(
        current_macro_numeric_chart_coverage=coverage,
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        current_data_refresh_ux=refresh_ux,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "current_data_refresh_ux" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["current_data_refresh_ux"]["research_only"] is True
    assert bundle["current_data_refresh_ux"]["current_data_refresh_ux_ready"] is True
    assert len(bundle["current_data_refresh_ux"]["refresh_cards"]) == 5
    assert (
        bundle["current_data_refresh_ux"]["live_refresh_executed_count"]
        == 0
    )
    assert bundle["current_data_refresh_ux"]["candidate_phase_emitted"] is False
    assert bundle["current_data_refresh_ux"]["current_phase_emitted"] is False
    assert validation["prohibited_action_field_count"] == 0


def test_research_dashboard_bundle_accepts_phase_start_confirmation() -> None:
    confirmation = build_declared_phase_start_confirmation_view_model()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        declared_phase_start_confirmation=confirmation,
    )
    validation = validate_research_dashboard_bundle(bundle)

    assert validation["bundle_schema_valid"] is True
    assert "declared_phase_start_confirmation" in {
        view["view_id"] for view in bundle["views"]
    }
    assert bundle["declared_phase_start_confirmation"]["research_only"] is True
    assert (
        bundle["declared_phase_start_confirmation"]["exact_start_date_confirmed"]
        is False
    )
    assert (
        bundle["declared_phase_start_confirmation"]["phase_age_precision_allowed"]
        is False
    )
    assert (
        bundle["declared_phase_start_confirmation"]["candidate_phase_emitted"]
        is False
    )
    assert (
        bundle["declared_phase_start_confirmation"]["current_phase_emitted"]
        is False
    )
    assert validation["prohibited_action_field_count"] == 0
