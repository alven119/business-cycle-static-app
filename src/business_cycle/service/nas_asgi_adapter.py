"""ASGI-compatible NAS app adapter skeleton for Phase 97.

The adapter wraps the Phase96 in-process app shell. It is intentionally a
pure-Python ASGI callable: no FastAPI dependency, no uvicorn run, no port bind,
and no database connection.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
import json
from typing import Any

import yaml

from business_cycle.service.nas_app_shell import (
    NasAppRequest,
    build_nas_app_shell,
    dispatch_nas_app_request,
    summarize_nas_app_shell,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_asgi_adapter_contract.yaml"

Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


class NasAsgiAdapter:
    """Small ASGI callable that delegates HTTP requests to the Phase96 shell."""

    def __init__(
        self,
        *,
        contract_path: str | Path = DEFAULT_CONTRACT_PATH,
        shell: dict[str, Any] | None = None,
    ) -> None:
        self.contract = load_nas_asgi_adapter_contract(contract_path)
        self.shell = shell or build_nas_app_shell()

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Receive,
        send: Send,
    ) -> None:
        """Handle one ASGI request without starting a live server."""

        _ = receive
        response = dispatch_asgi_scope(self.shell, scope, self.contract)
        await _send_response(send, response)


def load_nas_asgi_adapter_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase97 ASGI adapter contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_asgi_adapter_contract"])


def build_nas_asgi_adapter(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    shell: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Phase97 ASGI adapter readiness summary and smoke results."""

    contract = load_nas_asgi_adapter_contract(contract_path)
    shell = shell or build_nas_app_shell()
    adapter = NasAsgiAdapter(contract_path=contract_path, shell=shell)
    smoke = run_local_asgi_scope_smoke(adapter=adapter, contract=contract)
    summary: dict[str, Any] = {
        "phase": "97",
        "phase_id": 97,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase97_nas_asgi_adapter_skeleton",
        "artifact_version": contract["version"],
        "service_target": contract["service_scope"]["target_runtime"],
        "output_mode": "research_only_private_nas_asgi_adapter_smoke",
        "research_only": True,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "route_count": shell["route_count"],
        "nas_asgi_adapter_contract_ready": _contract_ready(contract),
        "phase96_shell_dependency_ready": _phase96_dependency_ready(),
        "asgi_scope_adapter_ready": _asgi_scope_adapter_ready(contract, adapter),
        "fastapi_mount_compatibility_ready": _fastapi_mount_compatible(
            contract,
            adapter,
        ),
        "uvicorn_run_attempt_count": 0,
        "network_bind_attempt_count": 0,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
        "trust_metadata": _trust_metadata(contract=contract, shell=shell),
    }
    summary |= smoke
    summary["local_asgi_smoke_ready"] = (
        summary["authenticated_asgi_smoke_pass_count"] == summary["route_count"]
        and summary["unauthenticated_asgi_smoke_rejected_count"]
        == summary["route_count"]
        and summary["unsupported_method_rejected_count"] == summary["route_count"]
        and summary["unknown_route_rejected_count"] == 1
    )
    summary["prohibited_output_field_count"] = _contains_prohibited_field(summary)
    summary["nas_asgi_adapter_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = "passed" if summary["nas_asgi_adapter_ready"] else "blocked"
    return summary


def dispatch_asgi_scope(
    shell: dict[str, Any],
    scope: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate an ASGI HTTP scope into the Phase96 shell request shape."""

    contract = contract or load_nas_asgi_adapter_contract()
    if scope.get("type") != contract["asgi_policy"]["supported_scope_type"]:
        return _json_response(400, {"error": "unsupported_scope_type"})
    method = str(scope.get("method", "")).upper()
    if method != contract["asgi_policy"]["supported_method"]:
        return _json_response(
            int(contract["asgi_policy"]["unsupported_method_status_code"]),
            {"error": "method_not_allowed", "research_only": True},
        )
    headers = _headers_from_scope(scope, contract)
    request = NasAppRequest(
        path=str(scope.get("path", "")),
        method=method,
        headers=headers,
    )
    return dispatch_nas_app_request(shell, request)


def run_local_asgi_scope_smoke(
    *,
    adapter: NasAsgiAdapter | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run ASGI scope dispatch smoke without binding a port."""

    contract = contract or load_nas_asgi_adapter_contract()
    adapter = adapter or NasAsgiAdapter()
    shell = adapter.shell
    header_name = contract["asgi_policy"]["session_header_name"]
    header_value = contract["asgi_policy"]["local_smoke_session_marker"]
    authenticated = [
        dispatch_asgi_scope(
            shell,
            _scope(
                path=route["path"],
                method=route["method"],
                headers={header_name: header_value},
            ),
            contract,
        )
        for route in shell["routes"]
    ]
    unauthenticated = [
        dispatch_asgi_scope(
            shell,
            _scope(path=route["path"], method=route["method"], headers={}),
            contract,
        )
        for route in shell["routes"]
    ]
    unsupported_method = [
        dispatch_asgi_scope(
            shell,
            _scope(
                path=route["path"],
                method="POST",
                headers={header_name: header_value},
            ),
            contract,
        )
        for route in shell["routes"]
    ]
    unknown_route = [
        dispatch_asgi_scope(
            shell,
            _scope(
                path="/missing",
                method="GET",
                headers={header_name: header_value},
            ),
            contract,
        ),
    ]
    all_responses = authenticated + unauthenticated + unsupported_method + unknown_route
    return {
        "authenticated_asgi_smoke_pass_count": sum(
            response["status_code"]
            == int(contract["asgi_policy"]["authenticated_success_status_code"])
            for response in authenticated
        ),
        "unauthenticated_asgi_smoke_rejected_count": sum(
            response["status_code"]
            == int(contract["asgi_policy"]["unauthenticated_status_code"])
            for response in unauthenticated
        ),
        "unsupported_method_rejected_count": sum(
            response["status_code"]
            == int(contract["asgi_policy"]["unsupported_method_status_code"])
            for response in unsupported_method
        ),
        "unknown_route_rejected_count": sum(
            response["status_code"]
            == int(contract["asgi_policy"]["unknown_route_status_code"])
            for response in unknown_route
        ),
        "response_start_event_count": len(all_responses),
        "response_body_event_count": len(all_responses),
    }


def summarize_nas_asgi_adapter(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase97 ASGI adapter readiness fields."""

    adapter = build_nas_asgi_adapter(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_asgi_adapter_contract_ready",
        "nas_asgi_adapter_ready",
        "asgi_scope_adapter_ready",
        "fastapi_mount_compatibility_ready",
        "local_asgi_smoke_ready",
        "phase96_shell_dependency_ready",
        "route_count",
        "authenticated_asgi_smoke_pass_count",
        "unauthenticated_asgi_smoke_rejected_count",
        "unsupported_method_rejected_count",
        "unknown_route_rejected_count",
        "response_start_event_count",
        "response_body_event_count",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "prohibited_output_field_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "development_next_phase",
        "result",
    )
    return {key: adapter[key] for key in keys} | {"nas_asgi_adapter": adapter}


async def invoke_asgi_for_test(
    adapter: NasAsgiAdapter,
    scope: dict[str, Any],
) -> list[dict[str, Any]]:
    """Invoke the ASGI callable and collect emitted events for tests."""

    events: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(event: dict[str, Any]) -> None:
        events.append(event)

    await adapter(scope, receive, send)
    return events


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    policy = contract["asgi_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["asgi_adapter_allowed"] is True
        and scope["fastapi_mount_compatible"] is True
        and scope["in_process_asgi_scope_smoke_only"] is True
        and scope["fastapi_dependency_required_now"] is False
        and scope["uvicorn_run_allowed_now"] is False
        and scope["network_bind_allowed_now"] is False
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and policy["supported_scope_type"] == "http"
        and policy["supported_method"] == "GET"
        and policy["production_auth_ready"] is False
    )


def _phase96_dependency_ready() -> bool:
    summary = summarize_nas_app_shell()
    return (
        summary["result"] == "passed"
        and summary["nas_app_shell_ready"] is True
        and summary["route_count"] == 5
    )


def _asgi_scope_adapter_ready(
    contract: dict[str, Any],
    adapter: NasAsgiAdapter,
) -> bool:
    return (
        callable(adapter)
        and contract["asgi_policy"]["supported_scope_type"] == "http"
        and contract["asgi_policy"]["supported_method"] == "GET"
    )


def _fastapi_mount_compatible(
    contract: dict[str, Any],
    adapter: NasAsgiAdapter,
) -> bool:
    return (
        callable(adapter)
        and contract["service_scope"]["fastapi_mount_compatible"] is True
        and contract["service_scope"]["fastapi_dependency_required_now"] is False
    )


async def _send_response(send: Send, response: dict[str, Any]) -> None:
    body = str(response["body"]).encode("utf-8")
    headers = [
        (b"content-type", str(response["content_type"]).encode("utf-8")),
        (b"cache-control", b"no-store"),
    ]
    await send(
        {
            "type": "http.response.start",
            "status": int(response["status_code"]),
            "headers": headers,
        },
    )
    await send({"type": "http.response.body", "body": body, "more_body": False})


def _headers_from_scope(
    scope: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_key, raw_value in scope.get("headers", []):
        key = raw_key.decode("latin-1")
        value = raw_value.decode("latin-1")
        headers[key] = value
        headers[_title_header(key)] = value
    session_header = contract["asgi_policy"]["session_header_name"]
    lowered_session_header = session_header.lower()
    if lowered_session_header in headers:
        headers[session_header] = headers[lowered_session_header]
    return headers


def _title_header(value: str) -> str:
    return "-".join(part.capitalize() for part in value.split("-"))


def _scope(
    *,
    path: str,
    method: str,
    headers: dict[str, str],
) -> dict[str, Any]:
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


def _json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status_code": status_code,
        "content_type": "application/json",
        "body": json.dumps(payload, sort_keys=True),
        "auth_checked": False,
        "route_id": None,
    }


def _trust_metadata(contract: dict[str, Any], shell: dict[str, Any]) -> dict[str, Any]:
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": "asgi_adapter_skeleton_no_live_server",
        "source_shell_artifact_id": shell["artifact_id"],
        "asgi_scope_type": contract["asgi_policy"]["supported_scope_type"],
        "fastapi_mount_compatible": True,
        "fastapi_dependency_required_now": False,
        "uvicorn_run_attempted": False,
        "network_bind_attempted": False,
        "live_server_started": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_asgi_adapter_ready", None)
    return expected


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0
