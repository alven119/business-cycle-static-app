from __future__ import annotations

import subprocess
import sys

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle_with_production_readiness_rehearsal,
)
from business_cycle.render.research_dashboard_production_readiness_rehearsal import (
    build_research_dashboard_production_readiness_rehearsal_view_model,
    summarize_research_dashboard_production_readiness_rehearsal,
)


def test_research_dashboard_production_readiness_rehearsal_passes() -> None:
    summary = summarize_research_dashboard_production_readiness_rehearsal()

    assert summary["result"] == "passed"
    assert summary["research_dashboard_production_readiness_rehearsal_ready"] is True
    assert summary["dashboard_migration_rehearsal_ready"] is True
    assert summary["renderer_caveats_ready"] is True
    assert summary["rollback_checklist_ready"] is True
    assert summary["production_boundary_drill_ready"] is True
    assert summary["migration_rehearsal_step_count"] == 4
    assert summary["renderer_caveat_count"] == 6
    assert summary["rollback_checklist_item_count"] == 6
    assert summary["production_boundary_check_count"] == 8
    assert summary["production_boundary_violation_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["pages_workflow_change_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_research_dashboard_production_readiness_view_model_is_dashboard_ready() -> None:
    view_model = build_research_dashboard_production_readiness_rehearsal_view_model()

    assert view_model["view_id"] == "research_dashboard_production_readiness_rehearsal"
    assert view_model["research_only"] is True
    assert view_model["readiness_label"] == "research_dashboard_migration_rehearsal_only"
    assert view_model["migration_rehearsal_step_count"] == 4
    assert view_model["renderer_caveat_count"] == 6
    assert view_model["rollback_checklist_item_count"] == 6
    assert view_model["production_boundary_check_count"] == 8
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert "production_decision" in view_model["prohibited_uses"]


def test_research_dashboard_bundle_accepts_phase87_rehearsal_view() -> None:
    bundle = build_research_dashboard_bundle_with_production_readiness_rehearsal()

    assert "research_dashboard_production_readiness_rehearsal" in {
        view["view_id"] for view in bundle["views"]
    }
    rehearsal = bundle["research_dashboard_production_readiness_rehearsal"]
    assert rehearsal["research_dashboard_production_readiness_rehearsal_ready"] is True
    assert rehearsal["production_boundary_violation_count"] == 0
    assert bundle["artifact_consistency"]["prohibited_action_field_count"] == 0


def test_show_research_dashboard_production_readiness_rehearsal_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_research_dashboard_production_readiness_rehearsal.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "research_dashboard_production_readiness_rehearsal_ready=true"
        in completed.stdout
    )
    assert "production_boundary_violation_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
