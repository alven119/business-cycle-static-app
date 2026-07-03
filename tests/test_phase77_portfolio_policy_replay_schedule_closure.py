from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase77_portfolio_policy_replay_schedule_closure import (
    summarize_phase77_portfolio_policy_replay_schedule_closure,
)


def test_phase77_portfolio_policy_replay_schedule_closure_passes() -> None:
    summary = summarize_phase77_portfolio_policy_replay_schedule_closure()

    assert summary["result"] == "passed"
    assert summary["phase77_closure_ready"] is True
    assert summary["portfolio_policy_replay_schedule_contract_ready"] is True
    assert summary["schedule_row_count"] == 8
    assert summary["template_with_schedule_count"] == 8
    assert summary["missing_template_schedule_count"] == 0
    assert summary["invalid_template_reference_count"] == 0
    assert summary["execution_allowed_now_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["portfolio_policy_replay_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["live_allocation_output_count"] == 0
    assert summary["score_interpretation_high_low_ready"] is True
    assert summary["role_with_score_interpretation_count"] == 39
    assert summary["score_interpretation_missing_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase77_closure_status"]
        == "closed_policy_replay_schedule_preregistered_score_interpretation_visible_no_execution"
    )


def test_show_phase77_portfolio_policy_replay_schedule_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase77_portfolio_policy_replay_schedule_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase77_closure_ready=true" in completed.stdout
    assert "schedule_row_count=8" in completed.stdout
    assert "role_with_score_interpretation_count=39" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
