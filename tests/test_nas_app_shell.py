from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.service.nas_app_shell import (
    NasAppRequest,
    build_nas_app_shell,
    dispatch_nas_app_request,
    summarize_nas_app_shell,
)

pytestmark = pytest.mark.archive_regression


def test_nas_app_shell_summary_passes() -> None:
    summary = summarize_nas_app_shell()

    assert summary["result"] == "passed"
    assert summary["nas_app_shell_contract_ready"] is True
    assert summary["nas_app_shell_ready"] is True
    assert summary["local_service_smoke_ready"] is True
    assert summary["phase95_dashboard_dependency_ready"] is True
    assert summary["auth_boundary_ready"] is True
    assert summary["route_dispatch_ready"] is True
    assert summary["service_health_ready"] is True
    assert summary["rollback_checklist_ready"] is True
    assert summary["route_count"] == 5
    assert summary["session_required_route_count"] == 5
    assert summary["authenticated_smoke_pass_count"] == 5
    assert summary["unauthenticated_smoke_rejected_count"] == 5
    assert summary["service_health_status"] == "ok"
    assert summary["service_health_route_count"] == 5


def test_nas_app_shell_dispatch_enforces_local_session_boundary() -> None:
    shell = build_nas_app_shell()
    header_name = shell["auth_policy"]["session_header_name"]
    header_value = shell["auth_policy"]["local_smoke_session_marker"]

    for route in shell["routes"]:
        unauthenticated = dispatch_nas_app_request(
            shell,
            NasAppRequest(path=route["path"], method=route["method"], headers={}),
        )
        authenticated = dispatch_nas_app_request(
            shell,
            NasAppRequest(
                path=route["path"],
                method=route["method"],
                headers={header_name: header_value},
            ),
        )

        assert unauthenticated["status_code"] == 401
        assert authenticated["status_code"] == 200
        assert authenticated["auth_checked"] is True
        assert authenticated["route_id"] == route["route_id"]


def test_nas_app_shell_preserves_no_live_boundaries() -> None:
    shell = build_nas_app_shell()
    health = shell["service_health_payload"]

    assert shell["network_bind_attempt_count"] == 0
    assert shell["live_server_start_attempt_count"] == 0
    assert shell["live_db_connection_attempt_count"] == 0
    assert shell["postgres_write_attempt_count"] == 0
    assert shell["live_fetch_attempt_count"] == 0
    assert shell["repo_output_written_count"] == 0
    assert shell["public_output_count"] == 0
    assert shell["frontend_database_access_allowed"] is False
    assert shell["frontend_api_key_allowed"] is False
    assert shell["candidate_phase_emitted"] is False
    assert shell["current_phase_emitted"] is False
    assert shell["prohibited_output_field_count"] == 0
    assert health["status"] == "ok"
    assert health["live_server_started"] is False
    assert health["live_db_connected"] is False
    assert health["postgres_write_attempted"] is False
    assert health["public_exposure"] is False


def test_nas_app_shell_rollback_checklist_is_ready() -> None:
    shell = build_nas_app_shell()
    steps = [row["step_id"] for row in shell["rollback_checklist"]]

    assert shell["rollback_checklist_item_count"] == 6
    assert steps == [
        "stop_private_nas_service",
        "restore_previous_git_checkout",
        "keep_postgres_data_volume_read_only",
        "validate_no_public_route_exposure",
        "rerun_local_service_smoke",
        "inspect_service_health_payload",
    ]
    assert all(row["ready_for_rehearsal"] is True for row in shell["rollback_checklist"])
    assert all(
        row["production_secret_required"] is False
        for row in shell["rollback_checklist"]
    )


def test_show_nas_app_shell_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_app_shell.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_app_shell_ready=true" in result.stdout
    assert "local_service_smoke_ready=true" in result.stdout
    assert "route_count=5" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_app_shell_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_nas_app_shell_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_app_shell_ready=true" in result.stdout
    assert "authenticated_smoke_pass_count=5" in result.stdout
    assert "unauthenticated_smoke_rejected_count=5" in result.stdout
    assert "live_server_start_attempt_count=0" in result.stdout
