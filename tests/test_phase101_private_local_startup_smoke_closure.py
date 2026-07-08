from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase101_private_local_startup_smoke_closure import (
    summarize_phase101_private_local_startup_smoke_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase101_private_local_startup_smoke_closure_passes() -> None:
    summary = summarize_phase101_private_local_startup_smoke_closure()

    assert summary["result"] == "passed"
    assert summary["phase101_closure_ready"] is True
    assert summary["nas_private_local_startup_smoke_ready"] is True
    assert summary["asgi_entrypoint_factory_ready"] is True
    assert summary["startup_plan_ready"] is True
    assert summary["startup_command_executed_count"] == 0
    assert summary["readiness_probe_pass_count"] == 5
    assert summary["uvicorn_run_attempt_count"] == 0
    assert summary["network_bind_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase101_closure_status"]
        == "closed_private_local_startup_smoke_ready_no_live_bind_or_db"
    )


def test_show_phase101_private_local_startup_smoke_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase101_private_local_startup_smoke_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase101_closure_ready=true" in result.stdout
    assert "nas_private_local_startup_smoke_ready=true" in result.stdout
    assert "startup_command_executed_count=0" in result.stdout
    assert "uvicorn_run_attempt_count=0" in result.stdout
    assert (
        "phase101_closure_status="
        "closed_private_local_startup_smoke_ready_no_live_bind_or_db"
    ) in result.stdout
    assert "result=passed" in result.stdout
