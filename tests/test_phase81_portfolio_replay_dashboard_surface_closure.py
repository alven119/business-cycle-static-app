from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase81_portfolio_replay_dashboard_surface_closure import (
    summarize_phase81_portfolio_replay_dashboard_surface_closure,
)


def test_phase81_portfolio_replay_dashboard_surface_closure_passes() -> None:
    summary = summarize_phase81_portfolio_replay_dashboard_surface_closure()

    assert summary["result"] == "passed"
    assert summary["phase81_closure_ready"] is True
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
    assert summary["product_capability_progress_ready"] is True
    assert summary["dashboard_view_contains_portfolio_replay_count"] == 1
    assert summary["rendered_portfolio_replay_page_count"] == 1
    assert summary["research_dashboard_runtime_ready"] is True
    assert summary["browser_verification_ready"] is True
    assert summary["missing_research_only_label_count"] == 0
    assert summary["prohibited_claim_count"] == 0
    assert summary["browser_missing_required_element_count"] == 0
    assert (
        summary["phase81_closure_status"]
        == "closed_portfolio_replay_dashboard_surface_ready_research_only"
    )


def test_show_phase81_portfolio_replay_dashboard_surface_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase81_portfolio_replay_dashboard_surface_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase81_closure_ready=true" in completed.stdout
    assert "portfolio_replay_dashboard_surface_ready=true" in completed.stdout
    assert "research_backtest_artifact_count=10" in completed.stdout
    assert "rendered_portfolio_replay_page_count=1" in completed.stdout
    assert "metric_value_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
