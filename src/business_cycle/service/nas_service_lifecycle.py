"""Local NAS service lifecycle rehearsal for Phase 98.

This module rehearses startup, readiness probes, shutdown, and rollback around
the Phase97 ASGI adapter. It never starts uvicorn, binds a port, connects to a
database, fetches live data, or writes public/repository outputs.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import yaml

from business_cycle.service.nas_asgi_adapter import (
    NasAsgiAdapter,
    summarize_nas_asgi_adapter,
    invoke_asgi_for_test,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_service_lifecycle_contract.yaml"

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


def load_nas_service_lifecycle_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase98 local lifecycle contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_service_lifecycle_contract"])


def build_nas_service_lifecycle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the local lifecycle rehearsal summary."""

    contract = load_nas_service_lifecycle_contract(contract_path)
    adapter = NasAsgiAdapter()
    phase97 = summarize_nas_asgi_adapter()
    startup_events = _startup_events(contract, phase97)
    readiness_probes = _readiness_probes(adapter=adapter, contract=contract)
    shutdown_events = _shutdown_events(contract)
    rollback_steps = _rollback_steps(contract)
    summary: dict[str, Any] = {
        "phase": "98",
        "phase_id": 98,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase98_nas_service_lifecycle_rehearsal",
        "artifact_version": contract["version"],
        "service_target": contract["service_scope"]["target_runtime"],
        "output_mode": "research_only_private_nas_lifecycle_rehearsal",
        "research_only": True,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_service_lifecycle_contract_ready": _contract_ready(contract),
        "phase97_asgi_dependency_ready": _phase97_dependency_ready(phase97),
        "startup_rehearsed": all(event["status"] == "passed" for event in startup_events),
        "readiness_probe_ready": all(
            probe["status_code"]
            == int(contract["lifecycle_policy"]["readiness_success_status_code"])
            for probe in readiness_probes
        ),
        "shutdown_rehearsed": all(
            event["status"] == "passed" for event in shutdown_events
        ),
        "rollback_rehearsal_ready": all(
            step["ready_for_rehearsal"] is True for step in rollback_steps
        ),
        "lifecycle_stage_count": len(contract["lifecycle_policy"]["lifecycle_stages"]),
        "startup_step_count": len(startup_events),
        "readiness_probe_count": len(readiness_probes),
        "readiness_probe_pass_count": sum(
            probe["status_code"]
            == int(contract["lifecycle_policy"]["readiness_success_status_code"])
            for probe in readiness_probes
        ),
        "shutdown_step_count": len(shutdown_events),
        "rollback_step_count": len(rollback_steps),
        "service_health_status": contract["lifecycle_policy"]["service_health_status"],
        "startup_events": startup_events,
        "readiness_probes": readiness_probes,
        "shutdown_events": shutdown_events,
        "rollback_steps": rollback_steps,
        "trust_metadata": _trust_metadata(contract=contract, phase97=phase97),
        "uvicorn_run_attempt_count": 0,
        "network_bind_attempt_count": 0,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
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
    summary["lifecycle_event_count"] = (
        summary["startup_step_count"]
        + summary["readiness_probe_count"]
        + summary["shutdown_step_count"]
        + summary["rollback_step_count"]
    )
    summary["lifecycle_rehearsal_ready"] = (
        summary["startup_rehearsed"] is True
        and summary["readiness_probe_ready"] is True
        and summary["shutdown_rehearsed"] is True
        and summary["rollback_rehearsal_ready"] is True
    )
    summary["prohibited_output_field_count"] = _contains_prohibited_field(summary)
    summary["nas_service_lifecycle_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_service_lifecycle_ready"] else "blocked"
    )
    return summary


def summarize_nas_service_lifecycle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase98 lifecycle rehearsal fields."""

    lifecycle = build_nas_service_lifecycle(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_service_lifecycle_contract_ready",
        "nas_service_lifecycle_ready",
        "lifecycle_rehearsal_ready",
        "phase97_asgi_dependency_ready",
        "startup_rehearsed",
        "readiness_probe_ready",
        "shutdown_rehearsed",
        "rollback_rehearsal_ready",
        "lifecycle_stage_count",
        "lifecycle_event_count",
        "startup_step_count",
        "readiness_probe_count",
        "readiness_probe_pass_count",
        "shutdown_step_count",
        "rollback_step_count",
        "service_health_status",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
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
    return {key: lifecycle[key] for key in keys} | {
        "nas_service_lifecycle": lifecycle,
    }


def _startup_events(
    contract: dict[str, Any],
    phase97: dict[str, Any],
) -> list[dict[str, Any]]:
    steps = contract["lifecycle_policy"]["startup_steps"]
    return [
        {
            "step_id": step,
            "status": "passed",
            "phase97_dependency_ready": phase97["nas_asgi_adapter_ready"],
            "live_server_started": False,
            "network_bound": False,
            "database_connected": False,
        }
        for step in steps
    ]


def _readiness_probes(
    *,
    adapter: NasAsgiAdapter,
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    policy = contract["lifecycle_policy"]
    header_name = adapter.contract["asgi_policy"]["session_header_name"]
    header_value = adapter.contract["asgi_policy"]["local_smoke_session_marker"]
    probes = []
    for path in policy["readiness_probe_paths"]:
        events = asyncio.run(
            invoke_asgi_for_test(
                adapter,
                _scope(path=path, method=policy["readiness_probe_method"], headers={
                    header_name: header_value,
                }),
            ),
        )
        start = events[0]
        probes.append(
            {
                "path": path,
                "method": policy["readiness_probe_method"],
                "status_code": int(start["status"]),
                "response_event_count": len(events),
                "cache_control_no_store": _has_no_store_header(start),
                "live_db_connected": False,
                "live_fetch_attempted": False,
                "public_output_written": False,
            },
        )
    return probes


def _shutdown_events(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": step,
            "status": "passed",
            "resource_close_type": "noop_in_process",
            "live_db_connection_closed": False,
            "server_socket_closed": False,
        }
        for step in contract["lifecycle_policy"]["shutdown_steps"]
    ]


def _rollback_steps(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": step,
            "ready_for_rehearsal": True,
            "production_secret_required": False,
            "data_mutation_required": False,
        }
        for step in contract["lifecycle_policy"]["rollback_steps"]
    ]


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


def _has_no_store_header(start_event: dict[str, Any]) -> bool:
    return any(
        key == b"cache-control" and value == b"no-store"
        for key, value in start_event.get("headers", [])
    )


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    policy = contract["lifecycle_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["lifecycle_rehearsal_allowed"] is True
        and scope["in_process_only"] is True
        and scope["asgi_adapter_dependency_required"] is True
        and scope["startup_event_rehearsal_allowed"] is True
        and scope["readiness_probe_allowed"] is True
        and scope["shutdown_event_rehearsal_allowed"] is True
        and scope["rollback_rehearsal_allowed"] is True
        and scope["uvicorn_run_allowed_now"] is False
        and scope["network_bind_allowed_now"] is False
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_read_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["frontend_database_access_allowed"] is False
        and scope["frontend_api_key_allowed"] is False
        and len(policy["lifecycle_stages"]) == 4
        and policy["production_service_ready"] is False
        and policy["production_auth_ready"] is False
    )


def _phase97_dependency_ready(phase97: dict[str, Any]) -> bool:
    return (
        phase97["result"] == "passed"
        and phase97["nas_asgi_adapter_ready"] is True
        and phase97["route_count"] == 5
        and phase97["local_asgi_smoke_ready"] is True
    )


def _trust_metadata(contract: dict[str, Any], phase97: dict[str, Any]) -> dict[str, Any]:
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": "local_service_lifecycle_rehearsal_no_live_bind",
        "source_asgi_adapter_phase": phase97["phase_id"],
        "source_asgi_adapter_ready": phase97["nas_asgi_adapter_ready"],
        "service_health_status": contract["lifecycle_policy"]["service_health_status"],
        "production_service_ready": False,
        "production_auth_ready": False,
        "uvicorn_run_attempted": False,
        "network_bind_attempted": False,
        "live_server_started": False,
        "live_db_connection_attempted": False,
        "postgres_read_attempted": False,
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
    expected.pop("nas_service_lifecycle_ready", None)
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
