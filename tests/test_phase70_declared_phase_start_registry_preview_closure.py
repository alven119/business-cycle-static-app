from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase70_declared_phase_start_registry_preview_closure import (
    summarize_phase70_declared_phase_start_registry_preview_closure,
)


def test_phase70_declared_phase_start_registry_preview_closure_passes() -> None:
    summary = summarize_phase70_declared_phase_start_registry_preview_closure()

    assert summary["result"] == "passed"
    assert summary["phase70_declared_phase_start_registry_preview_ready"] is True
    assert summary["declared_phase_start_registry_update_preview_ready"] is True
    assert summary["intake_contract_ready"] is True
    assert summary["sample_exact_date_preview_valid"] is True
    assert summary["sample_window_preview_valid"] is True
    assert summary["missing_input_wait_state_valid"] is True
    assert summary["cli_preview_output_ready"] is True
    assert summary["cli_preview_output_under_tmp"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["future_registry_update_gate_required"] is True
    assert summary["exact_date_preview_can_compute_phase_age"] is True
    assert summary["window_preview_exact_age_allowed"] is False
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
    assert summary["product_capability_progress_impacted_count"] == 3
    assert (
        summary["phase70_closure_status"]
        == "closed_declared_phase_start_registry_preview_ready_no_registry_write"
    )


def test_show_phase70_declared_phase_start_registry_preview_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase70_declared_phase_start_registry_preview_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase70_declared_phase_start_registry_preview_ready=true" in completed.stdout
    assert "sample_exact_date_preview_valid=true" in completed.stdout
    assert "sample_window_preview_valid=true" in completed.stdout
    assert "registry_write_allowed=false" in completed.stdout
    assert "result=passed" in completed.stdout
