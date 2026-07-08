from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.service.nas_service_lifecycle import (
    build_nas_service_lifecycle,
    summarize_nas_service_lifecycle,
)

pytestmark = pytest.mark.archive_regression


def test_nas_service_lifecycle_summary_passes() -> None:
    summary = summarize_nas_service_lifecycle()

    assert summary["result"] == "passed"
    assert summary["nas_service_lifecycle_contract_ready"] is True
    assert summary["nas_service_lifecycle_ready"] is True
    assert summary["lifecycle_rehearsal_ready"] is True
    assert summary["phase97_asgi_dependency_ready"] is True
    assert summary["startup_rehearsed"] is True
    assert summary["readiness_probe_ready"] is True
    assert summary["shutdown_rehearsed"] is True
    assert summary["rollback_rehearsal_ready"] is True
    assert summary["lifecycle_stage_count"] == 4
    assert summary["lifecycle_event_count"] == 16
    assert summary["readiness_probe_count"] == 5
    assert summary["readiness_probe_pass_count"] == 5
    assert summary["service_health_status"] == "ready_for_local_mount_only"


def test_nas_service_lifecycle_readiness_probes_hit_asgi_adapter() -> None:
    lifecycle = build_nas_service_lifecycle()

    probes = lifecycle["readiness_probes"]
    assert [probe["status_code"] for probe in probes] == [200, 200, 200, 200, 200]
    assert all(probe["response_event_count"] == 2 for probe in probes)
    assert all(probe["cache_control_no_store"] is True for probe in probes)
    assert all(probe["live_db_connected"] is False for probe in probes)
    assert all(probe["live_fetch_attempted"] is False for probe in probes)
    assert all(probe["public_output_written"] is False for probe in probes)


def test_nas_service_lifecycle_preserves_no_live_boundaries() -> None:
    lifecycle = build_nas_service_lifecycle()

    assert lifecycle["uvicorn_run_attempt_count"] == 0
    assert lifecycle["network_bind_attempt_count"] == 0
    assert lifecycle["live_server_start_attempt_count"] == 0
    assert lifecycle["live_db_connection_attempt_count"] == 0
    assert lifecycle["postgres_read_attempt_count"] == 0
    assert lifecycle["postgres_write_attempt_count"] == 0
    assert lifecycle["live_fetch_attempt_count"] == 0
    assert lifecycle["repo_output_written_count"] == 0
    assert lifecycle["public_output_count"] == 0
    assert lifecycle["frontend_database_access_allowed"] is False
    assert lifecycle["frontend_api_key_allowed"] is False
    assert lifecycle["candidate_phase_emitted"] is False
    assert lifecycle["current_phase_emitted"] is False
    assert lifecycle["prohibited_output_field_count"] == 0


def test_show_nas_service_lifecycle_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_service_lifecycle.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_service_lifecycle_ready=true" in result.stdout
    assert "readiness_probe_pass_count=5" in result.stdout
    assert "service_health_status=ready_for_local_mount_only" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_service_lifecycle_rehearsal_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_nas_service_lifecycle_rehearsal.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_service_lifecycle_ready=true" in result.stdout
    assert "lifecycle_rehearsal_ready=true" in result.stdout
    assert "readiness_probe_pass_count=5" in result.stdout
    assert "live_server_start_attempt_count=0" in result.stdout
    assert "postgres_read_attempt_count=0" in result.stdout
