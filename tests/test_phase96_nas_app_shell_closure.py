from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase96_nas_app_shell_closure import (
    summarize_phase96_nas_app_shell_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase96_nas_app_shell_closure_passes() -> None:
    summary = summarize_phase96_nas_app_shell_closure()

    assert summary["result"] == "passed"
    assert summary["phase96_closure_ready"] is True
    assert summary["nas_app_shell_contract_ready"] is True
    assert summary["nas_app_shell_ready"] is True
    assert summary["local_service_smoke_ready"] is True
    assert summary["auth_boundary_ready"] is True
    assert summary["route_dispatch_ready"] is True
    assert summary["service_health_ready"] is True
    assert summary["rollback_checklist_ready"] is True
    assert summary["route_count"] == 5
    assert summary["authenticated_smoke_pass_count"] == 5
    assert summary["unauthenticated_smoke_rejected_count"] == 5
    assert summary["rollback_checklist_item_count"] == 6
    assert summary["network_bind_attempt_count"] == 0
    assert summary["live_server_start_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["live_fetch_attempt_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["progress_decrease_count"] == 0
    assert summary["phase96_closure_status"] == (
        "closed_nas_app_shell_local_service_smoke_ready_no_live_server_or_db"
    )


def test_show_phase96_nas_app_shell_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase96_nas_app_shell_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase96_closure_ready=true" in result.stdout
    assert "nas_app_shell_ready=true" in result.stdout
    assert "local_service_smoke_ready=true" in result.stdout
    assert "progress_decrease_count=0" in result.stdout
    assert "result=passed" in result.stdout
