from __future__ import annotations

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
