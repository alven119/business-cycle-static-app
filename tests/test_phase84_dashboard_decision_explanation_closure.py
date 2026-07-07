from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase84_dashboard_decision_explanation_closure import (
    summarize_phase84_dashboard_decision_explanation_closure,
)


def test_phase84_dashboard_decision_explanation_closure_passes() -> None:
    summary = summarize_phase84_dashboard_decision_explanation_closure()

    assert summary["result"] == "passed"
    assert summary["phase84_closure_ready"] is True
    assert summary["sprint_roadmap_ready"] is True
    assert summary["dashboard_decision_explanation_ready"] is True
    assert summary["latest_evidence_dashboard_page_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["narrative_card_count"] == 5
    assert summary["decision_explanation_card_count"] == 5
    assert summary["dashboard_trust_caveat_count"] == 5
    assert summary["role_drilldown_count"] == 39
    assert summary["major_group_drilldown_count"] == 24
    assert summary["current_numeric_context_role_count"] == 37
    assert summary["chart_available_role_count"] == 37
    assert summary["group_ready_for_formal_phase_count"] == 0
    assert summary["browser_verification_ready"] is True
    assert summary["browser_missing_required_element_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["development_next_phase"] == 85
    assert summary["phase84_closure_status"] == (
        "closed_dashboard_decision_explanation_polished_no_phase_output"
    )


def test_show_phase84_dashboard_decision_explanation_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase84_dashboard_decision_explanation_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase84_closure_ready=true" in completed.stdout
    assert "dashboard_decision_explanation_ready=true" in completed.stdout
    assert "decision_explanation_card_count=5" in completed.stdout
    assert (
        "phase84_closure_status="
        "closed_dashboard_decision_explanation_polished_no_phase_output"
    ) in completed.stdout
    assert "result=passed" in completed.stdout
