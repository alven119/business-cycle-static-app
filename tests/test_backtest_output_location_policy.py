from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_output_location_policy,
    summarize_backtest_output_location_policy,
    validate_backtest_output_location_policy,
)

POLICY_PATH = Path("specs/portfolio/backtest_output_location_policy.yaml")


def test_backtest_output_location_policy_yaml_can_be_loaded() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)

    assert policy.version == 1
    assert policy.status == "draft"
    validate_backtest_output_location_policy(policy)


def test_backtest_output_location_policy_summary_blocks_writes() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)
    summary = summarize_backtest_output_location_policy(policy)

    assert summary["future_controlled_research_path_count"] >= 1
    assert summary["prohibited_auto_write_location_count"] >= 10
    assert summary["write_precondition_count"] >= 8
    assert summary["write_result_files_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["create_output_directories_allowed"] is False
    assert summary["execute_backtest_allowed"] is False
    assert summary["compute_metric_values_allowed"] is False
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["default_write_allowed_now"] is False
    assert summary["public_sync_allowed_now"] is False
    assert summary["git_track_result_files_allowed_now"] is False
    assert summary["phase_9a3_closure_status"] == "output_location_policy_design_only"
    assert summary["recommended_next_phase"] == "9A4"


def test_backtest_output_location_policy_future_path_requires_explicit_writer() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)
    paths = policy.future_controlled_research_paths[
        "allowed_only_after_future_writer_phase"
    ]
    research_path = next(item for item in paths if item["path"] == "data/backtests/research")

    assert research_path["auto_publication_allowed"] is False
    assert research_path["git_tracking_allowed"] is False
    assert research_path["requires_explicit_user_command"] is True


def test_backtest_output_location_policy_prohibits_auto_write_locations() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)

    assert {
        "public",
        "docs",
        "site",
        "dashboard",
        "github_pages",
        "data/backtests",
        "data/raw",
        "specs",
        "src",
        "tests",
    }.issubset(set(policy.prohibited_auto_write_locations))


def test_backtest_output_location_policy_requires_safety_dependencies() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)

    assert {
        "backtest_result_safety_validator",
        "backtest_result_caveat_policy",
        "explicit_output_writer_contract",
    }.issubset(set(policy.required_safety_dependencies))


def test_backtest_output_location_policy_prohibits_unsafe_written_fields() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(policy.prohibited_result_fields_for_any_written_output))


def test_backtest_output_location_policy_caveats_include_not_investment_advice() -> None:
    policy = load_backtest_output_location_policy(POLICY_PATH)

    assert any("不構成投資建議" in caveat for caveat in policy.caveats_zh)
