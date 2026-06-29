from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase45_declared_cycle_state_closure import (
    summarize_phase45_declared_cycle_state_closure,
)


def test_phase45_closure_hard_gates_pass() -> None:
    summary = summarize_phase45_declared_cycle_state_closure()

    assert summary["result"] == "passed"
    assert summary["declared_cycle_state_registry_ready"] is True
    assert summary["ordered_cycle_state_machine_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["legal_cycle_order_valid"] is True
    assert summary["illegal_transition_rejected_count"] > 0
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["legacy_v1_behavior_modified_count"] == 0
    assert summary["portfolio_policy_output_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase45_closure_script_outputs_passed_result() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase45_declared_cycle_state_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase_id=45" in completed.stdout
    assert "cycle_state_machine_alignment_status=declared_registry_and_legal_order_ready" in (
        completed.stdout
    )
    assert "result=passed" in completed.stdout
