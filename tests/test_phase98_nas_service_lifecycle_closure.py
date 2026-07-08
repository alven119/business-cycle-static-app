from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase98_nas_service_lifecycle_closure import (
    summarize_phase98_nas_service_lifecycle_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase98_nas_service_lifecycle_closure_passes() -> None:
    summary = summarize_phase98_nas_service_lifecycle_closure()

    assert summary["result"] == "passed"
    assert summary["phase98_closure_ready"] is True
    assert summary["nas_service_lifecycle_ready"] is True
    assert summary["lifecycle_rehearsal_ready"] is True
    assert summary["phase97_asgi_dependency_ready"] is True
    assert summary["readiness_probe_pass_count"] == 5
    assert summary["service_health_status"] == "ready_for_local_mount_only"
    assert summary["uvicorn_run_attempt_count"] == 0
    assert summary["network_bind_attempt_count"] == 0
    assert summary["live_server_start_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_read_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase98_closure_status"]
        == "closed_nas_service_lifecycle_rehearsal_ready_no_live_bind_or_db"
    )


def test_show_phase98_nas_service_lifecycle_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase98_nas_service_lifecycle_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase98_closure_ready=true" in result.stdout
    assert "nas_service_lifecycle_ready=true" in result.stdout
    assert "lifecycle_rehearsal_ready=true" in result.stdout
    assert "readiness_probe_pass_count=5" in result.stdout
    assert (
        "phase98_closure_status="
        "closed_nas_service_lifecycle_rehearsal_ready_no_live_bind_or_db"
    ) in result.stdout
    assert "result=passed" in result.stdout
