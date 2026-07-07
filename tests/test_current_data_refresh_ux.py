from __future__ import annotations

import subprocess
import sys

from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux,
    build_current_data_refresh_ux_view_model,
    summarize_current_data_refresh_ux,
)


def test_current_data_refresh_ux_passes() -> None:
    summary = summarize_current_data_refresh_ux()

    assert summary["result"] == "passed"
    assert summary["current_data_refresh_ux_ready"] is True
    assert summary["refresh_mode_summary_ready"] is True
    assert summary["last_update_summary_ready"] is True
    assert summary["freshness_summary_ready"] is True
    assert summary["source_risk_refresh_summary_ready"] is True
    assert summary["manual_refresh_handoff_ready"] is True
    assert summary["refresh_ux_card_count"] == 5
    assert summary["manual_refresh_handoff_step_count"] == 5
    assert summary["refresh_trust_caveat_count"] == 5
    assert summary["role_count"] == 39
    assert summary["role_with_numeric_context_count"] == 37
    assert summary["role_with_available_chart_payload_count"] == 37
    assert summary["role_without_official_series_count"] == 2
    assert summary["source_risk_visible_role_count"] == 39
    assert summary["elevated_source_risk_role_count"] == 21
    assert summary["live_refresh_executed_count"] == 0
    assert summary["live_fetch_attempt_count"] == 0
    assert summary["repository_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_current_data_refresh_ux_preserves_research_boundaries() -> None:
    artifact = build_current_data_refresh_ux()

    assert artifact["output_mode"] == "research_only_current_data_refresh_ux"
    assert artifact["trust_metadata"]["live_refresh_attempted"] is False
    assert artifact["trust_metadata"]["live_refresh_executed"] is False
    assert artifact["trust_metadata"]["point_in_time_result"] is False
    assert artifact["trust_metadata"]["current_phase_inference_enabled"] is False
    assert artifact["trust_metadata"]["candidate_phase_selection_enabled"] is False
    assert artifact["refresh_mode_summary"]["live_refresh_attempted"] is False
    assert artifact["refresh_mode_summary"]["live_refresh_executed"] is False
    assert "formal_current_phase_decision" in artifact["prohibited_uses"]
    assert "portfolio_or_trade_decision" in artifact["prohibited_uses"]


def test_current_data_refresh_ux_view_model_is_bundle_ready() -> None:
    view_model = build_current_data_refresh_ux_view_model()

    assert view_model["view_id"] == "current_data_refresh_ux"
    assert view_model["current_data_refresh_ux_ready"] is True
    assert len(view_model["refresh_cards"]) == 5
    assert len(view_model["manual_refresh_handoff_steps"]) == 5
    assert len(view_model["trust_caveats"]) == 5
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_show_current_data_refresh_ux_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_current_data_refresh_ux.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_data_refresh_ux_ready=true" in completed.stdout
    assert "refresh_ux_card_count=5" in completed.stdout
    assert "manual_refresh_handoff_step_count=5" in completed.stdout
    assert "live_refresh_executed_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
