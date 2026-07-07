from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase83_indicator_trend_drilldown_closure import (
    summarize_phase83_indicator_trend_drilldown_closure,
)


def test_phase83_indicator_trend_drilldown_closure_passes() -> None:
    summary = summarize_phase83_indicator_trend_drilldown_closure()

    assert summary["result"] == "passed"
    assert summary["phase83_closure_ready"] is True
    assert summary["sprint_roadmap_ready"] is True
    assert summary["indicator_trend_drilldown_navigation_ready"] is True
    assert summary["indicator_trend_chart_rendering_ready"] is True
    assert summary["role_drilldown_count"] == 39
    assert summary["current_chart_coverage_row_count"] == 39
    assert summary["role_trend_target_count"] == 39
    assert summary["role_trend_shortcut_count"] == 39
    assert summary["coverage_trend_link_count"] == 39
    assert summary["indicator_trend_link_count"] == 78
    assert summary["ytd_trend_period_card_count"] == 39
    assert summary["trailing_1y_trend_period_card_count"] == 39
    assert summary["trailing_5y_trend_period_card_count"] == 39
    assert summary["ytd_trend_svg_count"] == 37
    assert summary["trailing_1y_trend_svg_count"] == 37
    assert summary["trailing_5y_trend_svg_count"] == 37
    assert summary["available_trend_svg_count"] == 111
    assert summary["unavailable_chart_role_count"] == 2
    assert summary["trend_unavailable_empty_state_count"] == 6
    assert summary["browser_verification_ready"] is True
    assert summary["browser_missing_required_element_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["development_next_phase"] == 84
    assert summary["phase83_closure_status"] == (
        "closed_indicator_trend_drilldown_navigation_and_charts_ready"
    )


def test_show_phase83_indicator_trend_drilldown_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase83_indicator_trend_drilldown_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase83_closure_ready=true" in completed.stdout
    assert "indicator_trend_drilldown_navigation_ready=true" in completed.stdout
    assert "available_trend_svg_count=111" in completed.stdout
    assert (
        "phase83_closure_status="
        "closed_indicator_trend_drilldown_navigation_and_charts_ready"
    ) in completed.stdout
    assert "result=passed" in completed.stdout
