from __future__ import annotations

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    summarize_research_dashboard_bundle,
    validate_research_dashboard_bundle,
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
