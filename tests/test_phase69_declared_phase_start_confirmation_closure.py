from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase69_declared_phase_start_confirmation_closure import (
    summarize_phase69_declared_phase_start_confirmation_closure,
)


def test_phase69_declared_phase_start_confirmation_closure_passes() -> None:
    summary = summarize_phase69_declared_phase_start_confirmation_closure()

    assert summary["result"] == "passed"
    assert summary["phase69_declared_phase_start_confirmation_ready"] is True
    assert summary["declared_phase_start_confirmation_ready"] is True
    assert summary["dashboard_phase_start_confirmation_view_ready"] is True
    assert summary["rendered_phase_start_confirmation_ready"] is True
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
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_capability_progress_impacted_count"] == 5
    assert (
        summary["phase69_closure_status"]
        == "closed_declared_phase_start_confirmation_package_ready_registry_unchanged"
    )


def test_show_phase69_declared_phase_start_confirmation_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase69_declared_phase_start_confirmation_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase69_declared_phase_start_confirmation_ready=true" in completed.stdout
    assert "rendered_phase_start_confirmation_ready=true" in completed.stdout
    assert "candidate_start_window_count=3" in completed.stdout
    assert "phase_age_precision_allowed=false" in completed.stdout
    assert "registry_write_allowed=false" in completed.stdout
    assert "result=passed" in completed.stdout
