from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.product_capability_95_roadmap import (
    TARGET_CAPABILITY_IDS,
    summarize_product_capability_95_roadmap,
)
from business_cycle.audits.product_capability_100_completion_plan import (
    summarize_product_capability_100_completion_plan,
)
from business_cycle.audits.phase75_all_capability_roadmap_portfolio_research_closure import (
    summarize_phase75_all_capability_roadmap_portfolio_research_closure,
)


def test_product_capability_95_roadmap_passes() -> None:
    summary = summarize_product_capability_95_roadmap()

    assert summary["result"] == "passed"
    assert summary["roadmap_ready"] is True
    assert summary["target_capability_count"] == 8
    assert set(summary["target_capability_ids"]) == TARGET_CAPABILITY_IDS
    assert summary["planned_phase_count"] <= summary["max_phase_count"]
    assert summary["planned_phase_count"] == 10
    assert summary["target_phase_id"] == 84
    assert summary["prior_enabler_count"] == 10
    assert summary["prior_enabler_phase_ids"] == [
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
    ]
    assert summary["phase65_test_suite_reduction_enabler_present"] is True
    assert summary["phase66_archive_shard_enabler_present"] is True
    assert summary["phase67_transition_timing_enabler_present"] is True
    assert summary["phase68_test_index_and_numeric_overlay_enabler_present"] is True
    assert summary["phase69_start_confirmation_enabler_present"] is True
    assert summary["phase70_registry_preview_enabler_present"] is True
    assert summary["phase71_registry_update_gate_enabler_present"] is True
    assert summary["phase72_current_macro_numeric_chart_enabler_present"] is True
    assert summary["phase73_dashboard_method_explanation_enabler_present"] is True
    assert summary["phase74_local_cache_enabler_present"] is True
    assert summary["phase75_84_plan_recorded"] is True
    assert summary["portfolio_policy_research_target_present"] is True
    assert summary["historical_replay_backtest_target_present"] is True
    assert summary["model_governance_target_present"] is True
    assert summary["all_target_capabilities_reach_95"] is True
    assert summary["monotonic_progress_targets"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_95_roadmap_targets_are_monotonic() -> None:
    summary = summarize_product_capability_95_roadmap()

    for row in summary["target_capabilities"]:
        previous = int(row["baseline_percent"])
        for _, value in sorted(
            row["phase_targets"].items(), key=lambda item: int(item[0])
        ):
            current = int(value)
            assert current >= previous
            previous = current
        assert previous >= 95


def test_product_capability_95_roadmap_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_product_capability_95_roadmap.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "roadmap_ready=True" in result.stdout
    assert "planned_phase_count=10" in result.stdout
    assert "phase65_test_suite_reduction_enabler_present=True" in result.stdout
    assert "phase66_archive_shard_enabler_present=True" in result.stdout
    assert "phase67_transition_timing_enabler_present=True" in result.stdout
    assert (
        "phase68_test_index_and_numeric_overlay_enabler_present=True"
        in result.stdout
    )
    assert "phase69_start_confirmation_enabler_present=True" in result.stdout
    assert "phase70_registry_preview_enabler_present=True" in result.stdout
    assert "phase71_registry_update_gate_enabler_present=True" in result.stdout
    assert (
        "phase72_current_macro_numeric_chart_enabler_present=True"
        in result.stdout
    )
    assert (
        "phase73_dashboard_method_explanation_enabler_present=True"
        in result.stdout
    )
    assert "phase74_local_cache_enabler_present=True" in result.stdout
    assert "phase75_84_plan_recorded=True" in result.stdout
    assert "portfolio_policy_research_target_present=True" in result.stdout
    assert "historical_replay_backtest_target_present=True" in result.stdout
    assert "model_governance_target_present=True" in result.stdout
    assert "all_target_capabilities_reach_95=True" in result.stdout


def test_phase75_all_capability_roadmap_portfolio_research_closure_passes() -> None:
    summary = summarize_phase75_all_capability_roadmap_portfolio_research_closure()

    assert summary["result"] == "passed"
    assert summary["phase75_all_capability_roadmap_portfolio_research_ready"] is True
    assert summary["all_capability_95_roadmap_ready"] is True
    assert summary["portfolio_policy_research_baseline_contract_ready"] is True
    assert summary["target_capability_count"] == 8
    assert summary["planned_phase_count"] == 10
    assert summary["required_policy_template_count"] == 8
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["backtest_execution_count"] == 0


def test_phase75_all_capability_roadmap_portfolio_research_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase75_all_capability_roadmap_portfolio_research_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase75_all_capability_roadmap_portfolio_research_ready=true" in result.stdout
    assert "target_capability_count=8" in result.stdout
    assert "phase75_closure_status=closed_all_capability_95_roadmap_reset_portfolio_research_baseline_ready" in result.stdout


def test_product_capability_100_completion_plan_records_minimum_route() -> None:
    summary = summarize_product_capability_100_completion_plan()

    assert summary["result"] == "passed"
    assert summary["product_capability_100_completion_plan_ready"] is True
    assert summary["minimum_engineering_phase_count"] == 5
    assert summary["planned_phase_count"] == 5
    assert summary["planned_phase_ids"] == [87, 88, 89, 90, 91]
    assert summary["all_target_capabilities_reach_100"] is True
    assert summary["monotonic_progress_targets"] is True
    assert summary["calendar_prospective_validation_gate_required"] is True
    assert summary["calendar_gate_cannot_be_bypassed_by_phase_work"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_100_completion_plan_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_product_capability_100_completion_plan.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "product_capability_100_completion_plan_ready=True" in result.stdout
    assert "minimum_engineering_phase_count=5" in result.stdout
    assert "planned_phase_ids=[87, 88, 89, 90, 91]" in result.stdout
    assert "calendar_prospective_validation_gate_required=True" in result.stdout
