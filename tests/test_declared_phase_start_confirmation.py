from __future__ import annotations

import subprocess
import sys

from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation,
    build_declared_phase_start_confirmation_view_model,
    summarize_declared_phase_start_confirmation,
)


def test_declared_phase_start_confirmation_passes_without_registry_write() -> None:
    summary = summarize_declared_phase_start_confirmation()

    assert summary["result"] == "passed"
    assert summary["declared_phase_start_confirmation_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["candidate_start_window_count"] >= 2
    assert summary["user_prior_window_visible"] is True
    assert summary["evidence_based_window_abstains"] is True
    assert summary["exact_start_date_confirmed"] is False
    assert summary["start_window_confirmed"] is False
    assert summary["phase_age_precision_allowed"] is False
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_declared_phase_start_confirmation_windows_are_risk_labeled() -> None:
    artifact = build_declared_phase_start_confirmation()

    assert artifact["prohibited_output_field_count"] == 0
    assert {row["window_id"] for row in artifact["candidate_start_windows"]} >= {
        "user_prior_before_mid_2025",
        "user_prior_apr_may_2026_revision_window",
        "evidence_based_window_abstained",
    }
    assert all(
        row["can_compute_exact_phase_age"] is False
        for row in artifact["candidate_start_windows"]
    )
    assert all(
        row["may_modify_declared_registry"] is False
        for row in artifact["candidate_start_windows"]
    )


def test_declared_phase_start_confirmation_view_model_is_dashboard_ready() -> None:
    view_model = build_declared_phase_start_confirmation_view_model()

    assert view_model["view_id"] == "declared_phase_start_confirmation"
    assert view_model["research_only"] is True
    assert view_model["candidate_start_window_count"] >= 2
    assert view_model["phase_age_precision_allowed"] is False
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["production_behavior_change_count"] == 0


def test_show_declared_phase_start_confirmation_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_declared_phase_start_confirmation.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "declared_phase_start_confirmation_ready=true" in completed.stdout
    assert "candidate_start_window_count=3" in completed.stdout
    assert "phase_age_precision_allowed=false" in completed.stdout
    assert "registry_write_allowed=false" in completed.stdout
    assert "result=passed" in completed.stdout
