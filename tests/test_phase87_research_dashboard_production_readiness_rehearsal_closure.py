from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase87_research_dashboard_production_readiness_rehearsal_closure import (
    summarize_phase87_research_dashboard_production_readiness_rehearsal_closure,
)


def test_phase87_research_dashboard_production_readiness_rehearsal_closure_passes() -> None:
    summary = summarize_phase87_research_dashboard_production_readiness_rehearsal_closure()

    assert summary["result"] == "passed"
    assert summary["phase87_closure_ready"] is True
    assert summary["product_capability_100_completion_plan_ready"] is True
    assert summary["research_dashboard_production_readiness_rehearsal_ready"] is True
    assert summary["dashboard_rehearsal_view_ready"] is True
    assert summary["rendered_rehearsal_ready"] is True
    assert summary["html_migration_rehearsal_step_count"] == 4
    assert summary["html_renderer_caveat_count"] == 6
    assert summary["html_rollback_checklist_item_count"] == 6
    assert summary["html_production_boundary_check_count"] == 8
    assert summary["production_boundary_violation_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["development_next_phase"] == 88
    assert (
        summary["phase87_closure_status"]
        == "closed_research_dashboard_migration_rehearsal_ready_no_production_wiring"
    )


def test_show_phase87_research_dashboard_production_readiness_rehearsal_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase87_research_dashboard_production_readiness_rehearsal_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase87_closure_ready=true" in completed.stdout
    assert "dashboard_rehearsal_view_ready=true" in completed.stdout
    assert "production_boundary_violation_count=0" in completed.stdout
    assert "development_next_phase=88" in completed.stdout
    assert "result=passed" in completed.stdout
