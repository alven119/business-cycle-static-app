from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase46_boom_transition_monitor_closure import (
    summarize_phase46_boom_transition_monitor_closure,
)


def test_phase46_closure_preserves_doctrine_boundaries() -> None:
    summary = summarize_phase46_boom_transition_monitor_closure()

    assert summary["result"] == "passed"
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert summary["cycle_state_machine_alignment_status"] in {
        "declared_registry_used_by_boom_transition_monitor",
        "boom_transition_monitor_evidence_wired",
    }
    assert summary["legal_transition_semantics_preserved"] is True
    assert summary["phase_start_research_assistant_added_to_future_plan"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["portfolio_policy_output_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_boom_transition_monitor_script_outputs_passed_result() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_boom_transition_monitor.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "boom_transition_monitor_runtime_ready=true" in completed.stdout
    assert "declared_current_phase=boom" in completed.stdout
    assert "legal_next_phase=recession" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase46_closure_script_outputs_future_phase_start_plan() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase46_boom_transition_monitor_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase_start_research_assistant_added_to_future_plan=true" in completed.stdout
    assert "next_recommended_phase=Phase47_phase_start_research_assistant" in (
        completed.stdout
    )
    assert "result=passed" in completed.stdout
