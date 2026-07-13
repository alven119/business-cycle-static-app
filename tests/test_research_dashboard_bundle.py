from __future__ import annotations

from datetime import date
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
from business_cycle.render.phase_aware_dashboard_context import (
    build_phase_aware_dashboard_context,
    summarize_phase_aware_dashboard_context,
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
from business_cycle.audits.phase127_prospective_calendar_gate_closure import (
    summarize_phase127_prospective_calendar_gate_closure,
)
from business_cycle.audits.phase133_historical_transition_policy_timeline_closure import (
    summarize_phase133_historical_transition_policy_timeline_closure,
)
from business_cycle.audits.phase134_release_aware_source_identity_closure import (
    summarize_phase134_release_aware_source_identity_closure,
)
from business_cycle.service.nas_release_aware_freshness import (
    build_release_aware_freshness,
    role_series_overrides,
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
    replay = lab["historical_replay"]
    assert replay["pit_gap_series_count"] == 7
    assert replay["governed_event_count"] == 9
    assert replay["revised_pit_visual_separation_ready"] is True
    assert sum(row["pit_status"] == "strict_complete" for row in replay["scenario_rows"]) == 2
    assert sum(
        row["pit_status"] == "partial_explicit_abstention"
        for row in replay["scenario_rows"]
    ) == 3


def test_phase132_four_declared_contexts_preserve_legal_order() -> None:
    summary = summarize_phase_aware_dashboard_context()
    expected = {
        "recession": "recovery",
        "recovery": "growth",
        "growth": "boom",
        "boom": "recession",
    }

    assert summary["result"] == "passed"
    assert summary["phase_context_count"] == 4
    for phase, legal_next in expected.items():
        context = build_phase_aware_dashboard_context(
            {
                "declared_current_phase": phase,
                "declared_phase_start_display_zh": "synthetic",
                "phase_age_status": "synthetic",
                "active_registry_hash": f"test-{phase}",
            }
        )
        assert context["legal_next_phase"] == legal_next
        assert len(context["priority_role_ids"]) == 5
        assert any(
            row["lane_type"] == "transition_watch"
            for row in context["transition_lanes"]
        )
        assert any(
            row["lane_type"] == "transition_confirmation"
            for row in context["transition_lanes"]
        )
        assert context["automatic_state_change_allowed"] is False
        assert context["candidate_phase_emitted"] is False
        assert context["current_phase_emitted"] is False


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
        {
            "nav_id": "portfolio_research",
            "label_zh": "配置研究",
            "path": "/portfolio-research",
            "enabled": True,
        },
        {
            "nav_id": "historical_replay",
            "label_zh": "歷史重播",
            "path": "/historical-replay",
            "enabled": True,
        },
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
    assert lab["phase133_historical_policy_timeline_connected"] is True
    assert lab["phase133_monthly_annotation_count"] == 156
    assert lab["phase133_fixed_weight_sensitivity_result_count"] == 12
    assert lab["portfolio_research"]["full_cycle_policy_context_ready"] is True
    assert len(lab["portfolio_research"]["full_cycle_policy_rows"]) == 4
    assert lab["portfolio_research"]["quantitative_template_result_count"] == 6
    assert lab["portfolio_research"]["evidence_context_only_template_count"] == 2
    assert lab["portfolio_research"]["current_policy_context"]["book_rule_zh"]
    assert len(lab["portfolio_research"]["sensitivity_scenario_summaries"]) == 2
    assert "現在的配置研究該看什麼" in portfolio_html
    assert "防守能降低多少風險" in portfolio_html
    assert "查看 12 組固定參數的完整結果" in portfolio_html
    assert "不排序、不挑選歷史最佳結果" in portfolio_html
    assert "查看四階段配置邏輯" in portfolio_html
    assert "尚待 Phase 125" not in portfolio_html
    assert "Phase 125 結果" not in portfolio_html
    assert "如果站在當時，資料會告訴我什麼" in replay_html
    assert "當月可以怎麼判讀" in replay_html
    assert "後來發生了什麼" in replay_html
    assert "書籍政策回放" in replay_html
    assert "事件與 provenance" not in replay_html
    assert "查看觀察指標、資料缺口與事件來源" in replay_html
    assert 'class="provenance-list"' in replay_html
    assert 'class="technical-wrap"' in replay_html
    assert "boom_claims_u_shape" not in replay_html.split(
        '<script type="application/json" id="replay-scenarios">', 1
    )[0]
    assert "PIT 缺口，不輸出正式轉折結論" in replay_html
    assert lab["historical_replay"]["governed_event_count"] == 9
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False


def test_phase133_historical_annotations_and_sensitivity_preserve_doctrine() -> None:
    summary = summarize_phase133_historical_transition_policy_timeline_closure()
    timeline = summary["timeline"]

    assert summary["result"] == "passed"
    assert summary["scenario_count"] == 5
    assert summary["monthly_annotation_count"] == 156
    assert summary["nber_recession_annotation_month_count"] == 28
    assert summary["fixed_weight_sensitivity_result_count"] == 12
    assert summary["cash_flow_metric_provenance_complete_count"] == 12
    assert summary["recovery_cost_result_count"] == 6
    assert summary["false_derisk_cost_result_count"] == 6
    assert summary["private_nas_mobile_acceptance_passed"] is True
    assert summary["book_policy_state_transition_cause_count"] == 0
    assert summary["fixed_weight_result_rule_tuning_count"] == 0
    assert summary["best_historical_result_selected_count"] == 0
    assert summary["historical_label_runtime_usage_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert all(
        row["reference_phase_age_month"] is None
        for row in timeline["monthly_annotations"]
        if row["reference_cycle_state"] != "recession"
    )
    assert all(
        row["result_used_for_rule_tuning"] is False
        and row["selected_as_best_historical_result"] is False
        for row in timeline["fixed_weight_sensitivity_rows"]
    )


def test_phase134_release_aware_freshness_and_source_identity_are_integrated() -> None:
    windows = {
        "daily": 10,
        "weekly": 21,
        "monthly": 75,
        "quarterly": 180,
        "annual": 550,
    }
    monthly = build_release_aware_freshness(
        series_id="BUSINV",
        latest_observation_date=date(2026, 4, 1),
        as_of=date(2026, 7, 13),
        frequency="monthly",
        freshness_windows=windows,
    )
    quarterly = build_release_aware_freshness(
        series_id="PNFIC1",
        latest_observation_date=date(2026, 1, 1),
        as_of=date(2026, 7, 13),
        frequency="quarterly",
        freshness_windows=windows,
    )
    overrides = role_series_overrides()
    summary = summarize_phase134_release_aware_source_identity_closure()

    assert monthly["freshness_status"] == "fresh"
    assert monthly["reference_period_end_date"] == "2026-04-30"
    assert monthly["expected_reference_period"] == "2026-04"
    assert quarterly["freshness_status"] == "fresh"
    assert quarterly["reference_period_end_date"] == "2026-03-31"
    assert overrides["growth_adp_employment"] == ["ADPMNUSNERSA"]
    assert overrides["growth_private_nonresidential_fixed_investment"] == [
        "PNFIC1"
    ]
    assert overrides["growth_real_disposable_income_vs_consumption"] == [
        "DSPIC96",
        "PCEC96",
    ]
    assert summary["result"] == "passed"
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


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


def test_phase127_wait_surface_is_calendar_gated_and_does_not_write_or_seal() -> None:
    summary = summarize_phase127_prospective_calendar_gate_closure()

    assert summary["result"] == "passed"
    assert summary["prospective_wait_state_contract_ready"] is True
    assert summary["prospective_wait_state_page_ready"] is True
    assert summary["current_wait_state"] == "awaiting_canonical_as_of"
    assert summary["protocol_started"] is False
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["prospective_validation_seal_ready"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


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
