from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.product_capability_completion_sprint import (
    summarize_product_capability_completion_sprint,
)


def test_product_capability_completion_sprint_passes() -> None:
    summary = summarize_product_capability_completion_sprint()

    assert summary["result"] == "passed"
    assert summary["sprint_roadmap_ready"] is True
    assert summary["planned_phase_count"] == 5
    assert summary["planned_phase_ids"] == [83, 84, 85, 86, 87]
    assert summary["target_phase_id"] == 87
    assert summary["focus_capability_count"] == 3
    assert summary["focus_capabilities_reach_100"] is True
    assert summary["dashboard_usability_target_percent"] == 100
    assert summary["phase83_indicator_trend_drilldown_present"] is True
    assert summary["phase87_migration_rehearsal_present"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_completion_sprint_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_product_capability_completion_sprint.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "sprint_roadmap_ready=true" in completed.stdout
    assert "planned_phase_count=5" in completed.stdout
    assert "target_phase_id=87" in completed.stdout
    assert "phase83_indicator_trend_drilldown_present=true" in completed.stdout
    assert "phase87_migration_rehearsal_present=true" in completed.stdout
    assert "result=passed" in completed.stdout
