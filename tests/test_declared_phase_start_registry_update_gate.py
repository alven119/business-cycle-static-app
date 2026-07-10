from __future__ import annotations

import json
import subprocess
import sys

import pytest

from business_cycle.audits.phase113_nas_declared_phase_start_governance_closure import (
    summarize_phase113_nas_declared_phase_start_governance_closure,
)
from business_cycle.cycle_state.declared_phase_registry import load_declared_cycle_state
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate,
    build_declared_phase_start_registry_update_gate_view_model,
    summarize_declared_phase_start_registry_update_gate,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    APPLY_CONFIRMATION,
    ROLLBACK_CONFIRMATION,
    NasDeclaredPhaseStartError,
    apply_nas_declared_phase_start_update,
    build_nas_declared_phase_start_status,
    preview_nas_declared_phase_start_update,
    rollback_nas_declared_phase_start_update,
    summarize_nas_declared_phase_start_governance_contract,
)


def test_declared_phase_start_registry_update_gate_summary_passes() -> None:
    summary = summarize_declared_phase_start_registry_update_gate()

    assert summary["result"] == "passed"
    assert summary["declared_phase_start_registry_update_gate_ready"] is True
    assert summary["sample_exact_tmp_registry_update_valid"] is True
    assert summary["sample_window_tmp_registry_update_valid"] is True
    assert summary["missing_input_update_rejected"] is True
    assert summary["phase_age_dashboard_handoff_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["exact_tmp_registry_phase_age_days"] == 397
    assert summary["window_tmp_registry_exact_age_allowed"] is False
    assert summary["canonical_registry_write_allowed"] is False
    assert summary["canonical_registry_modified"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_exact_date_update_writes_tmp_registry_without_canonical_write(tmp_path) -> None:
    output = tmp_path / "declared_cycle_state_registry.yaml"
    gate = build_declared_phase_start_registry_update_gate(
        exact_start_date="2025-06-01",
        confirmation_note="operator confirmed exact start date",
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=output,
    )
    state = load_declared_cycle_state(output, as_of=None)

    assert gate["result"] == "passed"
    assert gate["tmp_registry_write_completed"] is True
    assert gate["canonical_registry_modified"] is False
    assert gate["exact_tmp_registry_phase_age_days"] == 397
    assert state.declared_phase_start_date.isoformat() == "2025-06-01"
    assert state.declared_phase_start_date_status == "user_confirmed_exact_date"


def test_bounded_window_update_writes_tmp_registry_without_exact_age(tmp_path) -> None:
    output = tmp_path / "declared_cycle_state_registry.yaml"
    gate = build_declared_phase_start_registry_update_gate(
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="operator confirmed bounded window",
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=output,
    )
    state = load_declared_cycle_state(output, as_of=None)

    assert gate["result"] == "passed"
    assert gate["tmp_registry_write_completed"] is True
    assert gate["window_tmp_registry_exact_age_allowed"] is False
    assert gate["phase_age_false_precision_count"] == 0
    assert state.declared_phase_start_date is None
    assert state.declared_phase_start_date_status == "user_confirmed_bounded_window"
    assert state.phase_age_status == "bounded_window_only_after_future_registry_update"


def test_missing_input_write_is_rejected(tmp_path) -> None:
    output = tmp_path / "declared_cycle_state_registry.yaml"
    gate = build_declared_phase_start_registry_update_gate(
        confirmation_note="operator tried without input",
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=output,
    )

    assert gate["result"] == "passed"
    assert gate["write_rejected"] is True
    assert "preview_not_valid" in gate["write_error_codes"]
    assert gate["tmp_registry_write_completed"] is False
    assert not output.exists()


def test_update_gate_view_model_is_dashboard_ready() -> None:
    view_model = build_declared_phase_start_registry_update_gate_view_model()

    assert view_model["view_id"] == "declared_phase_start_registry_update_gate"
    assert view_model["update_gate_ready"] is True
    assert view_model["canonical_registry_write_allowed"] is False
    assert view_model["future_canonical_registry_update_gate_required"] is True
    assert view_model["bounded_window_exact_age_allowed"] is False
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_apply_declared_phase_start_registry_update_script(tmp_path) -> None:
    registry_output = tmp_path / "declared_cycle_state_registry.yaml"
    result_output = tmp_path / "gate.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/apply_declared_phase_start_registry_update.py",
            "--start-date",
            "2025-06-01",
            "--as-of",
            "2026-07-03",
            "--confirmation-note",
            "test fixture",
            "--input-source",
            "test_fixture",
            "--write-temp-registry",
            "--registry-output",
            str(registry_output),
            "--output",
            str(result_output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result_output.read_text(encoding="utf-8"))

    assert registry_output.is_file()
    assert "declared_phase_start_registry_update_gate_ready=true" in completed.stdout
    assert "tmp_registry_write_completed=true" in completed.stdout
    assert "canonical_registry_write_allowed=false" in completed.stdout
    assert payload["exact_tmp_registry_phase_age_days"] == 397


def test_phase113_private_registry_preview_apply_stale_guard_and_rollback(
    tmp_path,
) -> None:
    summary = summarize_nas_declared_phase_start_governance_contract()
    active = tmp_path / "declared_cycle_state_registry.yaml"
    preview = preview_nas_declared_phase_start_update(
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="user confirmed bounded research window",
        as_of="2026-07-10",
        active_registry_path=active,
    )
    applied = apply_nas_declared_phase_start_update(
        preview_token=preview["preview_token"],
        confirmation=APPLY_CONFIRMATION,
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="user confirmed bounded research window",
        as_of="2026-07-10",
        active_registry_path=active,
    )
    status = build_nas_declared_phase_start_status(
        active_registry_path=active,
        as_of="2026-07-10",
    )

    assert summary["result"] == "passed"
    assert applied["apply_completed"] is True
    assert status["declared_current_phase"] == "boom"
    assert status["legal_next_phase"] == "recession"
    assert status["declared_phase_start_context_status"] == (
        "confirmed_bounded_window"
    )
    assert status["declared_phase_age_days"] is None
    assert status["declared_phase_age_range_days"] == {
        "minimum_days": 375,
        "maximum_days": 465,
    }
    with pytest.raises(NasDeclaredPhaseStartError, match="stale or mismatched"):
        apply_nas_declared_phase_start_update(
            preview_token=preview["preview_token"],
            confirmation=APPLY_CONFIRMATION,
            window_start_date="2025-04-01",
            window_end_date="2025-06-30",
            confirmation_note="user confirmed bounded research window",
            as_of="2026-07-10",
            active_registry_path=active,
        )
    rolled_back = rollback_nas_declared_phase_start_update(
        expected_active_hash=applied["after_hash"],
        confirmation=ROLLBACK_CONFIRMATION,
        active_registry_path=active,
        as_of="2026-07-10",
    )
    assert rolled_back["rollback_completed"] is True
    assert rolled_back["active_status"]["declared_phase_start_context_status"] == (
        "awaiting_user_confirmation"
    )


def test_phase113_live_closure_and_cli_pass() -> None:
    summary = summarize_phase113_nas_declared_phase_start_governance_closure()

    assert summary["result"] == "passed"
    assert summary["phase113_closure_ready"] is True
    assert summary["private_confirmation_workflow_deployed"] is True
    assert summary["active_registry_override_present"] is False
    assert summary["declared_phase_start_context_status"] == (
        "awaiting_user_confirmation"
    )
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["canonical_repository_registry_modified"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase113_nas_declared_phase_start_governance_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase113_closure_ready=true" in completed.stdout
    assert "user_confirmation_still_required=true" in completed.stdout
    assert "result=passed" in completed.stdout
