from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase97_nas_asgi_adapter_closure import (
    summarize_phase97_nas_asgi_adapter_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase97_nas_asgi_adapter_closure_passes() -> None:
    summary = summarize_phase97_nas_asgi_adapter_closure()

    assert summary["result"] == "passed"
    assert summary["phase97_closure_ready"] is True
    assert summary["nas_asgi_adapter_contract_ready"] is True
    assert summary["nas_asgi_adapter_ready"] is True
    assert summary["asgi_scope_adapter_ready"] is True
    assert summary["fastapi_mount_compatibility_ready"] is True
    assert summary["local_asgi_smoke_ready"] is True
    assert summary["phase96_shell_dependency_ready"] is True
    assert summary["route_count"] == 5
    assert summary["authenticated_asgi_smoke_pass_count"] == 5
    assert summary["unauthenticated_asgi_smoke_rejected_count"] == 5
    assert summary["unsupported_method_rejected_count"] == 5
    assert summary["unknown_route_rejected_count"] == 1
    assert summary["uvicorn_run_attempt_count"] == 0
    assert summary["live_server_start_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["live_fetch_attempt_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["progress_decrease_count"] == 0
    assert summary["phase97_closure_status"] == (
        "closed_nas_asgi_adapter_skeleton_ready_no_live_server_or_db"
    )


def test_show_phase97_nas_asgi_adapter_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase97_nas_asgi_adapter_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase97_closure_ready=true" in result.stdout
    assert "nas_asgi_adapter_ready=true" in result.stdout
    assert "local_asgi_smoke_ready=true" in result.stdout
    assert "progress_decrease_count=0" in result.stdout
    assert "result=passed" in result.stdout
