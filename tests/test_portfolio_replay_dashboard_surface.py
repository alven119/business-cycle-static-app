from __future__ import annotations

import subprocess
import sys

from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
    load_portfolio_replay_dashboard_surface_contract,
    summarize_portfolio_replay_dashboard_surface,
)


def test_phase81_portfolio_replay_dashboard_surface_passes() -> None:
    summary = summarize_portfolio_replay_dashboard_surface()

    assert summary["result"] == "passed"
    assert summary["portfolio_replay_dashboard_surface_ready"] is True
    assert summary["portfolio_replay_dashboard_view_model_ready"] is True
    assert summary["portfolio_replay_dashboard_bundle_integration_ready"] is True
    assert summary["portfolio_replay_dashboard_runtime_preview_ready"] is True
    assert summary["research_only_label_visible"] is True
    assert summary["scenario_count"] == 5
    assert summary["replay_data_mode_count"] == 2
    assert summary["research_backtest_artifact_count"] == 10
    assert summary["dashboard_card_count"] == 10
    assert summary["lineage_drilldown_row_count"] == 10
    assert summary["policy_schedule_reference_count"] == 10
    assert summary["cash_flow_kernel_reference_count"] == 10
    assert summary["metric_formula_reference_family_count"] == 11
    assert summary["metric_value_count"] == 0
    assert summary["risk_metric_value_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase81_view_model_is_research_only_with_lineage() -> None:
    view_model = build_portfolio_replay_dashboard_surface_view_model()

    assert view_model["view_id"] == "portfolio_replay_dashboard_surface"
    assert view_model["research_only"] is True
    assert view_model["research_only_label"] == "RESEARCH ONLY"
    assert len(view_model["dashboard_cards"]) == 10
    assert len(view_model["lineage_drilldown_rows"]) == 10
    assert all(row["input_hash"] for row in view_model["dashboard_cards"])
    assert all(
        row["source_metric_formula_registry_id"]
        for row in view_model["lineage_drilldown_rows"]
    )
    assert view_model["metric_value_count"] == 0
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_phase81_contract_disables_runtime_and_output_paths() -> None:
    contract = load_portfolio_replay_dashboard_surface_contract()

    assert contract["dashboard_view_model"]["output_mode"] == (
        "research_only_dashboard_surface"
    )
    assert contract["dashboard_view_model"]["research_only_label"] == "RESEARCH ONLY"
    assert all(value is False for value in contract["disabled_runtime_guards"].values())
    assert "current_allocation_guidance" in contract["dashboard_view_model"][
        "prohibited_uses"
    ]
    assert "public_output" in contract["dashboard_view_model"]["prohibited_uses"]


def test_show_portfolio_replay_dashboard_surface_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_portfolio_replay_dashboard_surface.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "portfolio_replay_dashboard_surface_ready=true" in completed.stdout
    assert "research_only_label_visible=true" in completed.stdout
    assert "research_backtest_artifact_count=10" in completed.stdout
    assert "metric_value_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
