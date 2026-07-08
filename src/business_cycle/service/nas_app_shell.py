"""In-process private NAS app shell smoke for Phase 96.

The shell rehearses route dispatch, session boundary, service health, and
rollback policy without starting a live server or touching a database.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

import yaml

from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    summarize_nas_service_dashboard,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_app_shell_contract.yaml"

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


@dataclass(frozen=True)
class NasAppRequest:
    """Tiny request object for in-process local smoke tests."""

    path: str
    method: str = "GET"
    headers: dict[str, str] | None = None


def load_nas_app_shell_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase96 NAS app shell contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_app_shell_contract"])


def build_nas_app_shell(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    dashboard_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an in-process app shell that dispatches Phase95 routes."""

    contract = load_nas_app_shell_contract(contract_path)
    dashboard = dashboard_bundle or build_nas_service_dashboard_bundle()
    routes = _route_table(contract=contract, dashboard=dashboard)
    rollback = _rollback_checklist(contract)
    shell: dict[str, Any] = {
        "phase": "96",
        "phase_id": 96,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase96_nas_app_shell_local_service_smoke",
        "artifact_version": contract["version"],
        "service_target": contract["service_scope"]["target_runtime"],
        "output_mode": "research_only_private_nas_app_shell_smoke",
        "research_only": True,
        "routes": routes,
        "route_count": len(routes),
        "session_required_route_count": sum(
            route["session_required"] is True for route in routes
        ),
        "auth_policy": _auth_policy(contract),
        "rollback_checklist": rollback,
        "rollback_checklist_item_count": len(rollback),
        "trust_metadata": _trust_metadata(contract=contract, dashboard=dashboard),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_app_shell_contract_ready": _contract_ready(contract),
        "phase95_dashboard_dependency_ready": _phase95_dependency_ready(),
        "auth_boundary_ready": _auth_boundary_ready(contract, routes),
        "route_dispatch_ready": _route_dispatch_ready(routes),
        "rollback_checklist_ready": len(rollback)
        == len(contract["rollback_policy"]["rollback_checklist"]),
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
    }
    smoke = run_local_service_smoke(shell=shell, contract=contract)
    shell |= smoke
    shell["service_health_ready"] = smoke["service_health_status"] == "ok"
    shell["nas_app_shell_ready"] = _passes(shell, _without_self(contract["hard_gates"]))
    shell["local_service_smoke_ready"] = (
        shell["authenticated_smoke_pass_count"] == shell["route_count"]
        and shell["unauthenticated_smoke_rejected_count"] == shell["route_count"]
        and shell["service_health_ready"] is True
    )
    shell["prohibited_output_field_count"] = _contains_prohibited_field(shell)
    shell["nas_app_shell_ready"] = _passes(shell, contract["hard_gates"])
    shell["result"] = "passed" if shell["nas_app_shell_ready"] else "blocked"
    return shell


def dispatch_nas_app_request(
    shell: dict[str, Any],
    request: NasAppRequest,
) -> dict[str, Any]:
    """Dispatch a local request through the in-process shell."""

    route = _find_route(shell["routes"], request.path, request.method)
    if route is None:
        return {
            "status_code": 404,
            "content_type": "application/json",
            "body": json.dumps({"error": "not_found"}, sort_keys=True),
            "auth_checked": False,
            "route_id": None,
        }
    if not _authorized(shell, request):
        return {
            "status_code": 401,
            "content_type": "application/json",
            "body": json.dumps(
                {
                    "error": "unauthorized",
                    "research_only": True,
                    "private_nas_only": True,
                },
                sort_keys=True,
            ),
            "auth_checked": True,
            "route_id": route["route_id"],
        }
    return {
        "status_code": 200,
        "content_type": route["content_type"],
        "body": route["body"],
        "auth_checked": True,
        "route_id": route["route_id"],
    }


def run_local_service_smoke(
    *,
    shell: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run authenticated and unauthenticated in-process smoke requests."""

    contract = contract or load_nas_app_shell_contract()
    session_header = contract["auth_policy"]["session_header_name"]
    session_marker = contract["auth_policy"]["local_smoke_session_marker"]
    authenticated = [
        dispatch_nas_app_request(
            shell,
            NasAppRequest(
                path=route["path"],
                method=route["method"],
                headers={session_header: session_marker},
            ),
        )
        for route in shell["routes"]
    ]
    unauthenticated = [
        dispatch_nas_app_request(
            shell,
            NasAppRequest(path=route["path"], method=route["method"], headers={}),
        )
        for route in shell["routes"]
    ]
    health = _service_health(shell, authenticated)
    return {
        "authenticated_smoke_pass_count": sum(
            response["status_code"] == 200 for response in authenticated
        ),
        "unauthenticated_smoke_rejected_count": sum(
            response["status_code"] == 401 for response in unauthenticated
        ),
        "service_health_status": health["status"],
        "service_health_route_count": health["route_count"],
        "service_health_payload": health,
    }


def summarize_nas_app_shell(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase96 app shell readiness fields."""

    shell = build_nas_app_shell(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_app_shell_contract_ready",
        "nas_app_shell_ready",
        "local_service_smoke_ready",
        "phase95_dashboard_dependency_ready",
        "auth_boundary_ready",
        "route_dispatch_ready",
        "service_health_ready",
        "rollback_checklist_ready",
        "route_count",
        "session_required_route_count",
        "authenticated_smoke_pass_count",
        "unauthenticated_smoke_rejected_count",
        "rollback_checklist_item_count",
        "service_health_status",
        "service_health_route_count",
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
    return {key: shell[key] for key in keys} | {"nas_app_shell": shell}


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    auth = contract["auth_policy"]
    rollback = contract["rollback_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["app_shell_allowed"] is True
        and scope["local_service_smoke_allowed"] is True
        and scope["in_process_dispatch_only"] is True
        and scope["network_bind_allowed_now"] is False
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["frontend_database_access_allowed"] is False
        and scope["frontend_api_key_allowed"] is False
        and auth["auth_boundary_required"] is True
        and auth["production_secret_embedded"] is False
        and auth["auth_is_production_ready"] is False
        and rollback["rollback_checklist_required"] is True
    )


def _phase95_dependency_ready() -> bool:
    summary = summarize_nas_service_dashboard()
    return (
        summary["result"] == "passed"
        and summary["nas_service_dashboard_ready"] is True
        and summary["route_count"] == 4
        and summary["api_payload_count"] == 3
    )


def _route_table(
    *,
    contract: dict[str, Any],
    dashboard: dict[str, Any],
) -> list[dict[str, Any]]:
    html_by_path = {page["path"]: page["html"] for page in dashboard["html_pages"]}
    api_by_path = {
        "/api/indicator-snapshot.json": dashboard["api_payloads"][
            "indicator_snapshot"
        ],
        "/api/service-status.json": dashboard["api_payloads"]["service_status"],
        "/api/indicator-index.json": dashboard["api_payloads"]["indicator_index"],
    }
    rows: list[dict[str, Any]] = []
    for route in contract["route_policy"]["routes"]:
        if route["output_kind"] == "html":
            body = html_by_path[route["path"]]
            content_type = "text/html; charset=utf-8"
        else:
            body = json.dumps(api_by_path[route["path"]], sort_keys=True)
            content_type = "application/json"
        rows.append(
            {
                "route_id": route["route_id"],
                "path": route["path"],
                "method": route["method"],
                "output_kind": route["output_kind"],
                "content_type": content_type,
                "body": body,
                "session_required": True,
                "private_nas_only": True,
                "frontend_database_access_allowed": False,
                "frontend_api_key_allowed": False,
            },
        )
    return rows


def _auth_policy(contract: dict[str, Any]) -> dict[str, Any]:
    auth = contract["auth_policy"]
    return {
        "auth_boundary_required": auth["auth_boundary_required"],
        "session_header_name": auth["session_header_name"],
        "local_smoke_session_marker": auth["local_smoke_session_marker"],
        "production_secret_embedded": auth["production_secret_embedded"],
        "auth_is_production_ready": auth["auth_is_production_ready"],
    }


def _rollback_checklist(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": step,
            "ready_for_rehearsal": True,
            "production_secret_required": False,
        }
        for step in contract["rollback_policy"]["rollback_checklist"]
    ]


def _auth_boundary_ready(contract: dict[str, Any], routes: list[dict[str, Any]]) -> bool:
    auth = contract["auth_policy"]
    return (
        auth["auth_boundary_required"] is True
        and auth["production_secret_embedded"] is False
        and all(route["session_required"] is True for route in routes)
    )


def _route_dispatch_ready(routes: list[dict[str, Any]]) -> bool:
    return all(route["body"] and route["content_type"] for route in routes)


def _find_route(
    routes: list[dict[str, Any]],
    path: str,
    method: str,
) -> dict[str, Any] | None:
    for route in routes:
        if route["path"] == path and route["method"] == method:
            return route
    return None


def _authorized(shell: dict[str, Any], request: NasAppRequest) -> bool:
    headers = request.headers or {}
    policy = shell["auth_policy"]
    return (
        headers.get(policy["session_header_name"])
        == policy["local_smoke_session_marker"]
    )


def _service_health(
    shell: dict[str, Any],
    authenticated_responses: list[dict[str, Any]],
) -> dict[str, Any]:
    all_ok = all(response["status_code"] == 200 for response in authenticated_responses)
    return {
        "status": "ok" if all_ok else "blocked",
        "route_count": shell["route_count"],
        "auth_boundary": "local_smoke_only",
        "live_server_started": False,
        "live_db_connected": False,
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "public_exposure": False,
        "research_only": True,
    }


def _trust_metadata(contract: dict[str, Any], dashboard: dict[str, Any]) -> dict[str, Any]:
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": "local_in_process_app_shell_smoke",
        "source_dashboard_bundle_hash": dashboard["bundle_hash"],
        "auth_boundary": "local_smoke_session_header",
        "auth_is_production_ready": False,
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


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_app_shell_ready", None)
    expected.pop("local_service_smoke_ready", None)
    expected.pop("service_health_ready", None)
    expected.pop("prohibited_output_field_count", None)
    return expected


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0
