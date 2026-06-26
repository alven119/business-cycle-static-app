from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase39_current_research_snapshot import (
    summarize_phase39_current_research_snapshot,
)


def test_phase39_current_research_snapshot_audit_passes() -> None:
    summary = summarize_phase39_current_research_snapshot()

    assert summary["result"] == "passed"
    assert summary["ci_safety_scan_context_allowlist_ready"] is True
    assert summary["unsupported_claim_false_positive_count"] == 0
    assert summary["phase37_clean_environment_deterministic"] is True
    assert summary["phase37_recession_recovery_pit_remediation_result"] == "passed"
    assert summary["phase37_closure_result"] == "passed"
    assert summary["current_snapshot_availability_ready"] is True
    assert summary["current_research_snapshot_runtime_ready"] is True
    assert summary["current_dashboard_view_ready"] is True
    assert summary["dashboard_view_count"] == 8
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_action_field_count"] == 0
    assert summary["production_behavior_change_count"] == 0


def test_show_phase39_current_research_snapshot_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase39_current_research_snapshot.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "current_dashboard_view_ready=true" in result.stdout
