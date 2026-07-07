from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase86_transition_risk_evidence_accumulation_closure import (
    summarize_phase86_transition_risk_evidence_accumulation_closure,
)


def test_phase86_transition_risk_evidence_accumulation_closure_passes() -> None:
    summary = summarize_phase86_transition_risk_evidence_accumulation_closure()

    assert summary["result"] == "passed"
    assert summary["phase86_closure_ready"] is True
    assert summary["transition_risk_evidence_accumulation_ready"] is True
    assert summary["latest_evidence_dashboard_page_ready"] is True
    assert summary["rendered_transition_risk_evidence_accumulation_ready"] is True
    assert summary["transition_accumulation_lane_card_count"] == 13
    assert summary["html_transition_accumulation_lane_card_count"] == 13
    assert summary["evidence_accumulation_event_count"] == 39
    assert summary["next_required_observation_count"] == 13
    assert summary["html_next_required_observation_count"] == 13
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["phase_presence_transition_separation_valid"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_action_field_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert (
        summary["phase86_closure_status"]
        == "closed_transition_risk_evidence_accumulation_view_ready_no_phase_selection"
    )


def test_show_phase86_transition_risk_evidence_accumulation_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase86_transition_risk_evidence_accumulation_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase86_closure_ready=true" in completed.stdout
    assert "transition_risk_evidence_accumulation_ready=true" in completed.stdout
    assert "html_transition_accumulation_lane_card_count=13" in completed.stdout
    assert "html_next_required_observation_count=13" in completed.stdout
    assert "result=passed" in completed.stdout
