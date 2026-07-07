from __future__ import annotations

import subprocess
import sys

from business_cycle.portfolio.replay_backtest_lineage_hardening import (
    build_replay_backtest_lineage_hardening_report,
    load_replay_backtest_lineage_hardening_contract,
)


def test_replay_backtest_lineage_hardening_report_passes() -> None:
    summary = build_replay_backtest_lineage_hardening_report()

    assert summary["result"] == "passed"
    assert summary["replay_backtest_lineage_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["replay_row_count"] == 10
    assert summary["research_backtest_artifact_count"] == 10
    assert summary["artifact_replay_row_link_count"] == 10
    assert summary["replay_row_missing_artifact_count"] == 0
    assert summary["artifact_without_replay_row_count"] == 0
    assert summary["source_contract_hash_family_count"] == 4
    assert summary["source_contract_hash_coverage_complete"] is True
    assert summary["source_contract_hash_mismatch_count"] == 0
    assert summary["artifact_with_complete_source_contract_hashes_count"] == 10
    assert summary["input_hash_coverage_complete"] is True
    assert summary["artifact_with_verified_input_hash_count"] == 10
    assert summary["deterministic_input_hash_count"] == 10
    assert summary["input_hash_mismatch_count"] == 0
    assert summary["unique_input_hash_count"] == 10
    assert summary["artifact_lineage_mismatch_count"] == 0
    assert summary["data_mode_separation_valid"] is True
    assert summary["strict_replay_row_count"] == 5
    assert summary["revised_replay_row_count"] == 5
    assert summary["silent_fallback_count"] == 0
    assert summary["missing_input_without_abstention_count"] == 0
    assert summary["abstention_without_reason_count"] == 0
    assert summary["revised_mislabeled_as_point_in_time_count"] == 0


def test_replay_backtest_lineage_hardening_keeps_outputs_research_only() -> None:
    summary = build_replay_backtest_lineage_hardening_report()

    assert summary["metric_value_count"] == 0
    assert summary["risk_metric_value_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["repository_output_count"] == 0
    assert summary["generated_output_under_tmp_only"] is True
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_replay_backtest_lineage_contract_disables_runtime_guards() -> None:
    contract = load_replay_backtest_lineage_hardening_contract()

    assert contract["phase_id"] == 82
    assert contract["lineage_policy"]["silent_fallback_allowed"] is False
    assert contract["lineage_policy"]["generated_repo_output_allowed"] is False
    assert all(value is False for value in contract["disabled_runtime_guards"].values())


def test_show_replay_backtest_lineage_hardening_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_replay_backtest_lineage_hardening.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "replay_backtest_lineage_ready=true" in completed.stdout
    assert "input_hash_coverage_complete=true" in completed.stdout
    assert "silent_fallback_count=0" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
