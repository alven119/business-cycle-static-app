"""DS925+ private-LAN read-only connectivity smoke for Phase 103.

The default path is a no-network preview so CI never depends on the user's
private LAN. A live probe is available only through an explicit flag and only
performs unauthenticated TCP connect attempts to governed ports.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any
import ipaddress
import json
import socket

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_ds925_connectivity_smoke_contract.yaml"
)

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
SECRET_MARKERS = ("PASSWORD", "SECRET", "API_KEY", "TOKEN")
Connector = Callable[[str, int, float], bool]


def load_nas_ds925_connectivity_smoke_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase103 connectivity smoke contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_ds925_connectivity_smoke_contract"])


def build_nas_ds925_connectivity_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    execute_live: bool = False,
    connector: Connector | None = None,
) -> dict[str, Any]:
    """Build the Phase103 endpoint registration and optional live smoke."""

    contract = load_nas_ds925_connectivity_smoke_contract(contract_path)
    endpoint = contract["target_endpoint"]
    scope = contract["probe_scope"]
    ip = str(endpoint["nas_private_ip"])
    ports = list(contract["probe_ports"])
    live_results = (
        _run_tcp_probe(
            ip,
            ports,
            timeout_seconds=float(scope["timeout_seconds"]),
            connector=connector or _tcp_connect,
        )
        if execute_live
        else []
    )
    probe_plan = _probe_plan(contract)
    summary: dict[str, Any] = {
        "phase": "103",
        "phase_id": 103,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase103_nas_ds925_connectivity_smoke",
        "artifact_version": contract["version"],
        "output_mode": "research_only_private_lan_connectivity_smoke",
        "research_only": True,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_private_ip": ip,
        "nas_private_ip_source": endpoint["ip_source"],
        "nas_private_ip_private_lan": _is_private_lan_ip(ip),
        "public_internet_exposure_default": bool(
            endpoint["public_internet_exposure_default"],
        ),
        "nas_ds925_connectivity_smoke_contract_ready": _contract_ready(contract),
        "nas_ds925_endpoint_registry_ready": _endpoint_registry_ready(contract),
        "probe_plan_ready": _probe_plan_ready(probe_plan),
        "probe_port_count": len(ports),
        "probe_plan": probe_plan,
        "live_probe_allowed_now": bool(scope["live_probe_allowed_now"]),
        "live_probe_requires_explicit_flag": bool(
            scope["live_probe_requires_explicit_flag"],
        ),
        "default_probe_execution_count": 0,
        "tests_network_dependency_count": 0,
        "live_probe_executed": execute_live,
        "live_probe_attempt_count": len(live_results),
        "live_probe_reachable_count": sum(item["reachable"] for item in live_results),
        "live_probe_unreachable_count": sum(
            not item["reachable"] for item in live_results
        ),
        "live_probe_results": live_results,
        "http_request_attempt_count": 0,
        "dsm_login_attempt_count": 0,
        "ssh_login_attempt_count": 0,
        "package_install_attempt_count": 0,
        "tailscale_login_attempt_count": 0,
        "container_manager_import_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_image_pull_attempt_count": 0,
        "container_start_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "secret_value_literal_count": _secret_value_literal_count(
            {
                "probe_plan": probe_plan,
                "live_probe_results": live_results,
            },
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "trust_metadata": _trust_metadata(contract, execute_live),
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        {
            "probe_plan": probe_plan,
            "live_probe_results": live_results,
            "trust_metadata": summary["trust_metadata"],
        },
    )
    summary["nas_ds925_connectivity_smoke_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_ds925_connectivity_smoke_ready"] else "blocked"
    )
    return summary


def summarize_nas_ds925_connectivity_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase103 no-network preview fields."""

    smoke = build_nas_ds925_connectivity_smoke(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_ds925_connectivity_smoke_contract_ready",
        "nas_ds925_connectivity_smoke_ready",
        "nas_ds925_endpoint_registry_ready",
        "nas_private_ip",
        "nas_private_ip_private_lan",
        "nas_private_ip_source",
        "public_internet_exposure_default",
        "probe_plan_ready",
        "probe_port_count",
        "live_probe_allowed_now",
        "live_probe_requires_explicit_flag",
        "default_probe_execution_count",
        "tests_network_dependency_count",
        "http_request_attempt_count",
        "dsm_login_attempt_count",
        "ssh_login_attempt_count",
        "package_install_attempt_count",
        "tailscale_login_attempt_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_image_pull_attempt_count",
        "container_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "secret_value_literal_count",
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
    return {key: smoke[key] for key in keys} | {
        "nas_ds925_connectivity_smoke": smoke,
    }


def write_nas_ds925_connectivity_smoke_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    execute_live: bool = False,
    connector: Connector | None = None,
) -> dict[str, Any]:
    """Write connectivity smoke artifacts under an explicit temporary path."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase103 connectivity smoke output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    smoke = build_nas_ds925_connectivity_smoke(
        contract_path=contract_path,
        execute_live=execute_live,
        connector=connector,
    )
    files = {
        "ds925-connectivity-probe-plan.json": smoke["probe_plan"],
        "ds925-connectivity-smoke-report.json": {
            key: value
            for key, value in smoke.items()
            if key not in {"probe_plan", "trust_metadata"}
        },
        "ds925-connectivity-trust-metadata.json": smoke["trust_metadata"],
    }
    written = []
    for filename, payload in files.items():
        path = output_path / filename
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(str(path))
    return {
        "nas_ds925_connectivity_smoke_ready": smoke[
            "nas_ds925_connectivity_smoke_ready"
        ],
        "connectivity_smoke_output_path_count": len(written),
        "connectivity_smoke_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "written_paths": written,
        "live_probe_executed": smoke["live_probe_executed"],
        "live_probe_attempt_count": smoke["live_probe_attempt_count"],
        "live_probe_reachable_count": smoke["live_probe_reachable_count"],
        "live_probe_unreachable_count": smoke["live_probe_unreachable_count"],
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if smoke["result"] == "passed" else "blocked",
    }


def _probe_plan(contract: dict[str, Any]) -> dict[str, Any]:
    scope = contract["probe_scope"]
    return {
        "phase": 103,
        "nas_private_ip": contract["target_endpoint"]["nas_private_ip"],
        "default_mode": scope["default_mode"],
        "execute_flag": scope["live_probe_execute_flag"],
        "timeout_seconds": scope["timeout_seconds"],
        "allowed_probe_kind": scope["allowed_probe_kind"],
        "ports": contract["probe_ports"],
        "live_probe_requires_explicit_flag": scope["live_probe_requires_explicit_flag"],
        "http_request_allowed_now": scope["http_request_allowed_now"],
        "authentication_allowed_now": False,
        "postgres_access_allowed_now": False,
        "repo_output_allowed_now": False,
    }


def _run_tcp_probe(
    ip: str,
    ports: list[dict[str, Any]],
    *,
    timeout_seconds: float,
    connector: Connector,
) -> list[dict[str, Any]]:
    results = []
    for item in ports:
        port = int(item["port"])
        try:
            reachable = bool(connector(ip, port, timeout_seconds))
            error = None
        except OSError as exc:
            reachable = False
            error = exc.__class__.__name__
        results.append(
            {
                "port_id": item["port_id"],
                "port": port,
                "probe_kind": "tcp_connect_without_authentication",
                "reachable": reachable,
                "error": error,
                "authentication_attempted": False,
                "http_request_attempted": False,
            },
        )
    return results


def _tcp_connect(ip: str, port: int, timeout_seconds: float) -> bool:
    with socket.create_connection((ip, port), timeout=timeout_seconds):
        return True


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["probe_scope"]
    return (
        contract["status"] == "active_research_contract"
        and scope["default_mode"] == "no_network_preview"
        and scope["live_probe_allowed_now"] is True
        and scope["live_probe_requires_explicit_flag"] is True
        and scope["allowed_probe_kind"] == "tcp_connect_without_authentication"
        and scope["http_request_allowed_now"] is False
        and scope["dsm_login_allowed_now"] is False
        and scope["package_install_allowed_now"] is False
        and scope["container_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
    )


def _endpoint_registry_ready(contract: dict[str, Any]) -> bool:
    endpoint = contract["target_endpoint"]
    return (
        str(endpoint["nas_private_ip"]) == "192.168.1.116"
        and endpoint["ip_source"] == "user_provided_phase103"
        and endpoint["private_lan_only"] is True
        and endpoint["public_internet_exposure_default"] is False
        and _is_private_lan_ip(str(endpoint["nas_private_ip"]))
    )


def _probe_plan_ready(plan: dict[str, Any]) -> bool:
    return (
        plan["default_mode"] == "no_network_preview"
        and plan["live_probe_requires_explicit_flag"] is True
        and plan["http_request_allowed_now"] is False
        and plan["authentication_allowed_now"] is False
        and len(plan["ports"]) == 4
    )


def _is_private_lan_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return bool(ip.version == 4 and ip.is_private)


def _secret_value_literal_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_secret_value_literal_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_secret_value_literal_count(item) for item in value)
    if isinstance(value, str):
        return int(
            any(marker in value for marker in SECRET_MARKERS)
            and "=" in value
            and "<" not in value
            and "${" not in value
        )
    return 0


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _trust_metadata(contract: dict[str, Any], execute_live: bool) -> dict[str, Any]:
    endpoint = contract["target_endpoint"]
    return {
        "nas_migration_surface": "ds925_private_lan_connectivity_smoke",
        "nas_private_ip": endpoint["nas_private_ip"],
        "ip_source": endpoint["ip_source"],
        "private_lan_only": endpoint["private_lan_only"],
        "live_probe_executed": execute_live,
        "probe_kind": "tcp_connect_without_authentication",
        "http_request_attempted": False,
        "dsm_login_attempted": False,
        "ssh_login_attempted": False,
        "package_install_attempted": False,
        "container_manager_import_attempted": False,
        "container_started": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _is_under_tmp(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == Path("/tmp") or Path("/tmp") in resolved.parents


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_ds925_connectivity_smoke_ready", None)
    return expected
