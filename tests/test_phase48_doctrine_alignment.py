from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase48_boom_transition_evidence_wiring_closure import (
    summarize_phase48_boom_transition_evidence_wiring_closure,
)


def test_phase48_closure_preserves_doctrine_boundaries() -> None:
    summary = summarize_phase48_boom_transition_evidence_wiring_closure()

    assert summary["result"] == "passed"
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert summary["cycle_state_machine_alignment_status"] == (
        "boom_transition_monitor_evidence_wired"
    )
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["required_priority_role_count"] == 5
    assert summary["wired_priority_role_count"] == 5
    assert summary["evaluable_priority_role_count"] > 0
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["recession_confirmation_not_derived_from_watch_only"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase48_wiring_script_outputs_passed_result() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_boom_transition_evidence_wiring.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "boom_transition_evidence_wiring_ready=true" in completed.stdout
    assert "required_priority_role_count=5" in completed.stdout
    assert "wired_priority_role_count=5" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase48_closure_script_outputs_passed_result() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase48_boom_transition_evidence_wiring_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase48_closure_status=closed_boom_transition_monitor" in (
        completed.stdout
    )
    assert "cycle_state_machine_alignment_status=boom_transition_monitor" in (
        completed.stdout
    )
    assert "result=passed" in completed.stdout
