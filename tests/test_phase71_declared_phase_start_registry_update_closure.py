from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase71_declared_phase_start_registry_update_closure import (
    summarize_phase71_declared_phase_start_registry_update_closure,
)


def test_phase71_declared_phase_start_registry_update_closure_passes() -> None:
    summary = summarize_phase71_declared_phase_start_registry_update_closure()

    assert summary["result"] == "passed"
    assert summary["phase71_declared_phase_start_registry_update_ready"] is True
    assert summary["declared_phase_start_registry_update_gate_ready"] is True
    assert summary["sample_exact_tmp_registry_update_valid"] is True
    assert summary["sample_window_tmp_registry_update_valid"] is True
    assert summary["missing_input_update_rejected"] is True
    assert summary["phase_age_dashboard_handoff_ready"] is True
    assert summary["rendered_phase_start_update_gate_ready"] is True
    assert summary["cli_tmp_registry_update_ready"] is True
    assert summary["cli_tmp_registry_output_under_tmp"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["exact_tmp_registry_phase_age_days"] == 397
    assert summary["window_tmp_registry_exact_age_allowed"] is False
    assert summary["canonical_registry_write_allowed"] is False
    assert summary["canonical_registry_modified"] is False
    assert summary["future_canonical_registry_update_gate_required"] is True
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
    assert summary["product_capability_progress_impacted_count"] == 4
    assert (
        summary["phase71_closure_status"]
        == "closed_declared_phase_start_registry_update_gate_ready_canonical_registry_unchanged"
    )


def test_show_phase71_declared_phase_start_registry_update_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase71_declared_phase_start_registry_update_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase71_declared_phase_start_registry_update_ready=true" in completed.stdout
    assert "sample_exact_tmp_registry_update_valid=true" in completed.stdout
    assert "sample_window_tmp_registry_update_valid=true" in completed.stdout
    assert "canonical_registry_write_allowed=false" in completed.stdout
    assert "result=passed" in completed.stdout
