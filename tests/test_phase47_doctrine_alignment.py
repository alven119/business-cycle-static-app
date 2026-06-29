from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase47_phase_start_research_assistant_closure import (
    summarize_phase47_phase_start_research_assistant_closure,
)


def test_phase47_closure_preserves_doctrine_boundaries() -> None:
    summary = summarize_phase47_phase_start_research_assistant_closure()

    assert summary["result"] == "passed"
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert summary["cycle_state_machine_alignment_status"] == (
        "phase_start_research_context_added_registry_unchanged"
    )
    assert summary["legal_transition_semantics_preserved"] is True
    assert summary["declared_registry_modified"] is False
    assert summary["registry_write_allowed"] is False
    assert summary["user_confirmation_required"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["portfolio_policy_output_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["phase48_boom_monitor_evidence_wiring_plan_ready"] is True


def test_phase_start_research_assistant_script_outputs_passed_result() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase_start_research_assistant.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase_start_research_assistant_runtime_ready=true" in completed.stdout
    assert "declared_current_phase=boom" in completed.stdout
    assert "registry_write_allowed=false" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase47_closure_script_outputs_phase48_plan() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase47_phase_start_research_assistant_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase48_boom_monitor_evidence_wiring_plan_ready=true" in completed.stdout
    assert "next_recommended_phase=Phase48_boom_monitor_evidence_wiring" in (
        completed.stdout
    )
    assert "result=passed" in completed.stdout
