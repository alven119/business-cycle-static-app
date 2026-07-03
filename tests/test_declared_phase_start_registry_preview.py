from __future__ import annotations

import json
import subprocess
import sys

from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    build_declared_phase_start_registry_update_preview,
    summarize_declared_phase_start_registry_update_preview,
)


def test_declared_phase_start_registry_preview_summary_passes() -> None:
    summary = summarize_declared_phase_start_registry_update_preview()

    assert summary["result"] == "passed"
    assert summary["declared_phase_start_registry_update_preview_ready"] is True
    assert summary["intake_contract_ready"] is True
    assert summary["sample_exact_date_preview_valid"] is True
    assert summary["sample_window_preview_valid"] is True
    assert summary["missing_input_wait_state_valid"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["future_registry_update_gate_required"] is True
    assert summary["exact_date_preview_can_compute_phase_age"] is True
    assert summary["window_preview_exact_age_allowed"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_exact_date_preview_computes_dry_run_age_without_registry_write() -> None:
    preview = build_declared_phase_start_registry_update_preview(
        exact_start_date="2025-06-01",
        confirmation_note="user would confirm this in a future gate",
        input_source="test_fixture",
        as_of="2026-07-03",
    )

    assert preview["preview_valid"] is True
    assert preview["input_precision"] == "exact_date"
    assert preview["can_compute_exact_phase_age"] is True
    assert preview["proposed_phase_age_days"] == 397
    assert preview["registry_patch_preview"]["declared_phase_start_date"] == "2025-06-01"
    assert preview["registry_write_allowed"] is False
    assert preview["declared_registry_modified"] is False
    assert preview["phase_age_false_precision_count"] == 0


def test_window_preview_preserves_range_and_blocks_exact_age() -> None:
    preview = build_declared_phase_start_registry_update_preview(
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="user would confirm this in a future gate",
        input_source="test_fixture",
        as_of="2026-07-03",
    )

    assert preview["preview_valid"] is True
    assert preview["input_precision"] == "bounded_window"
    assert preview["can_compute_exact_phase_age"] is False
    assert preview["proposed_phase_age_days"] is None
    assert preview["phase_age_window_days"] == {
        "minimum_days": 368,
        "maximum_days": 458,
    }
    assert preview["registry_patch_preview"]["declared_phase_start_date"] is None
    assert preview["phase_age_false_precision_count"] == 0


def test_missing_input_preview_waits_for_user_input() -> None:
    preview = build_declared_phase_start_registry_update_preview(as_of="2026-07-03")

    assert preview["preview_valid"] is False
    assert preview["input_wait_state"] is True
    assert preview["input_validation_status"] == "input_required"
    assert preview["input_validation_error_codes"] == ["start_input_required"]
    assert preview["registry_patch_preview"] is None
    assert preview["registry_write_allowed"] is False


def test_invalid_preview_rejects_mutual_exclusion_and_future_date() -> None:
    preview = build_declared_phase_start_registry_update_preview(
        exact_start_date="2026-08-01",
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        as_of="2026-07-03",
    )

    assert preview["preview_valid"] is False
    assert preview["input_validation_status"] == "invalid_input"
    assert "exact_date_and_window_are_mutually_exclusive" in preview[
        "input_validation_error_codes"
    ]
    assert "start_input_after_as_of" in preview["input_validation_error_codes"]
    assert preview["phase_age_false_precision_count"] == 0


def test_preview_declared_phase_start_registry_update_script(tmp_path) -> None:
    output_path = tmp_path / "phase70_preview.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/preview_declared_phase_start_registry_update.py",
            "--start-date",
            "2025-06-01",
            "--as-of",
            "2026-07-03",
            "--confirmation-note",
            "test fixture",
            "--input-source",
            "test_fixture",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert "declared_phase_start_registry_update_preview_ready=true" in completed.stdout
    assert "preview_valid=true" in completed.stdout
    assert "can_compute_exact_phase_age=true" in completed.stdout
    assert "registry_write_allowed=false" in completed.stdout
    assert payload["preview_valid"] is True
    assert payload["declared_registry_modified"] is False
