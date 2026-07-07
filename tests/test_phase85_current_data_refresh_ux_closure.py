from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase85_current_data_refresh_ux_closure import (
    summarize_phase85_current_data_refresh_ux_closure,
)


def test_phase85_current_data_refresh_ux_closure_passes() -> None:
    summary = summarize_phase85_current_data_refresh_ux_closure()

    assert summary["result"] == "passed"
    assert summary["phase85_closure_ready"] is True
    assert summary["sprint_roadmap_ready"] is True
    assert summary["current_data_refresh_ux_ready"] is True
    assert summary["latest_evidence_dashboard_page_ready"] is True
    assert summary["refresh_ux_card_count"] == 5
    assert summary["html_refresh_ux_card_count"] == 5
    assert summary["manual_refresh_handoff_step_count"] == 5
    assert summary["html_manual_refresh_handoff_step_count"] == 5
    assert summary["refresh_trust_caveat_count"] == 5
    assert summary["html_refresh_trust_caveat_count"] == 5
    assert summary["role_count"] == 39
    assert summary["role_with_numeric_context_count"] == 37
    assert summary["role_with_available_chart_payload_count"] == 37
    assert summary["source_risk_visible_role_count"] == 39
    assert summary["elevated_source_risk_role_count"] == 21
    assert summary["live_refresh_executed_count"] == 0
    assert summary["live_fetch_attempt_count"] == 0
    assert summary["browser_verification_ready"] is True
    assert summary["browser_missing_required_element_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["development_next_phase"] == 86
    assert summary["phase85_closure_status"] == (
        "closed_current_data_refresh_ux_hardened_no_live_execution"
    )


def test_show_phase85_current_data_refresh_ux_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase85_current_data_refresh_ux_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase85_closure_ready=true" in completed.stdout
    assert "current_data_refresh_ux_ready=true" in completed.stdout
    assert "html_refresh_ux_card_count=5" in completed.stdout
    assert (
        "phase85_closure_status="
        "closed_current_data_refresh_ux_hardened_no_live_execution"
    ) in completed.stdout
    assert "result=passed" in completed.stdout
