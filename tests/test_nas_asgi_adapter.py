from __future__ import annotations

import asyncio
import subprocess
import sys

import pytest

from business_cycle.service.nas_asgi_adapter import (
    NasAsgiAdapter,
    build_nas_asgi_adapter,
    dispatch_asgi_scope,
    invoke_asgi_for_test,
    summarize_nas_asgi_adapter,
)

pytestmark = pytest.mark.archive_regression


def test_nas_asgi_adapter_summary_passes() -> None:
    summary = summarize_nas_asgi_adapter()

    assert summary["result"] == "passed"
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
    assert summary["response_start_event_count"] == 16
    assert summary["response_body_event_count"] == 16


def test_nas_asgi_adapter_scope_translation_enforces_boundaries() -> None:
    adapter = build_nas_asgi_adapter()
    trust = adapter["trust_metadata"]
    assert trust["fastapi_mount_compatible"] is True
    assert trust["fastapi_dependency_required_now"] is False

    runtime = NasAsgiAdapter()
    header_name = runtime.contract["asgi_policy"]["session_header_name"]
    header_value = runtime.contract["asgi_policy"]["local_smoke_session_marker"]
    route = runtime.shell["routes"][0]

    authenticated = dispatch_asgi_scope(
        runtime.shell,
        _scope(route["path"], route["method"], {header_name: header_value}),
        runtime.contract,
    )
    unauthenticated = dispatch_asgi_scope(
        runtime.shell,
        _scope(route["path"], route["method"], {}),
        runtime.contract,
    )
    unsupported_method = dispatch_asgi_scope(
        runtime.shell,
        _scope(route["path"], "POST", {header_name: header_value}),
        runtime.contract,
    )
    unknown_route = dispatch_asgi_scope(
        runtime.shell,
        _scope("/missing", "GET", {header_name: header_value}),
        runtime.contract,
    )

    assert authenticated["status_code"] == 200
    assert unauthenticated["status_code"] == 401
    assert unsupported_method["status_code"] == 405
    assert unknown_route["status_code"] == 404


def test_nas_asgi_callable_emits_start_and_body_events() -> None:
    runtime = NasAsgiAdapter()
    header_name = runtime.contract["asgi_policy"]["session_header_name"]
    header_value = runtime.contract["asgi_policy"]["local_smoke_session_marker"]
    route = runtime.shell["routes"][0]

    events = asyncio.run(
        invoke_asgi_for_test(
            runtime,
            _scope(route["path"], route["method"], {header_name: header_value}),
        ),
    )

    assert [event["type"] for event in events] == [
        "http.response.start",
        "http.response.body",
    ]
    assert events[0]["status"] == 200
    assert events[1]["body"]


def test_nas_asgi_adapter_preserves_no_live_boundaries() -> None:
    adapter = build_nas_asgi_adapter()

    assert adapter["uvicorn_run_attempt_count"] == 0
    assert adapter["network_bind_attempt_count"] == 0
    assert adapter["live_server_start_attempt_count"] == 0
    assert adapter["live_db_connection_attempt_count"] == 0
    assert adapter["postgres_write_attempt_count"] == 0
    assert adapter["live_fetch_attempt_count"] == 0
    assert adapter["repo_output_written_count"] == 0
    assert adapter["public_output_count"] == 0
    assert adapter["frontend_database_access_allowed"] is False
    assert adapter["frontend_api_key_allowed"] is False
    assert adapter["candidate_phase_emitted"] is False
    assert adapter["current_phase_emitted"] is False
    assert adapter["prohibited_output_field_count"] == 0


def test_show_nas_asgi_adapter_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_asgi_adapter.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_asgi_adapter_ready=true" in result.stdout
    assert "local_asgi_smoke_ready=true" in result.stdout
    assert "route_count=5" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_asgi_adapter_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_nas_asgi_adapter_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_asgi_adapter_ready=true" in result.stdout
    assert "authenticated_asgi_smoke_pass_count=5" in result.stdout
    assert "unauthenticated_asgi_smoke_rejected_count=5" in result.stdout
    assert "unsupported_method_rejected_count=5" in result.stdout
    assert "live_server_start_attempt_count=0" in result.stdout


def _scope(path: str, method: str, headers: dict[str, str]) -> dict[str, object]:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "method": method,
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1"))
            for key, value in headers.items()
        ],
    }
