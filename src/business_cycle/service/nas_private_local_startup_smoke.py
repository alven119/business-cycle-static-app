"""Private local NAS service startup smoke for Phase 101.

This module validates the local startup shape from the Phase100 Container
Manager bundle and the Phase97 ASGI factory. It never runs uvicorn, binds a
port, imports the bundle into Container Manager, starts containers, connects to
Postgres, or writes repository outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml

from business_cycle.service.nas_asgi_adapter import (
    run_local_asgi_scope_smoke,
    summarize_nas_asgi_adapter,
)
from business_cycle.service.nas_container_manager_bundle import (
    build_nas_container_manager_bundle,
    summarize_nas_container_manager_bundle,
)
from business_cycle.service.nas_private_asgi_app import create_app
from business_cycle.service.nas_service_lifecycle import summarize_nas_service_lifecycle

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_private_local_startup_smoke_contract.yaml"
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


def load_nas_private_local_startup_smoke_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase101 private local startup smoke contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_private_local_startup_smoke_contract"])


def build_nas_private_local_startup_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase101 private local startup smoke summary."""

    contract = load_nas_private_local_startup_smoke_contract(contract_path)
    bundle_summary = summarize_nas_container_manager_bundle()
    bundle = build_nas_container_manager_bundle()
    lifecycle = summarize_nas_service_lifecycle()
    phase97 = summarize_nas_asgi_adapter()
    app = create_app()
    asgi_smoke = run_local_asgi_scope_smoke(adapter=app)
    startup_plan = _startup_plan(contract)
    rollback = _rollback_steps(contract)
    env_placeholders = contract["startup_plan"]["required_environment_placeholders"]
    summary: dict[str, Any] = {
        "phase": "101",
        "phase_id": 101,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase101_nas_private_local_startup_smoke",
        "artifact_version": contract["version"],
        "output_mode": "research_only_private_local_startup_smoke",
        "research_only": True,
        "target_device": contract["startup_scope"]["target_device"],
        "private_access_mode": contract["startup_scope"]["private_access_mode"],
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_private_local_startup_smoke_contract_ready": _contract_ready(contract),
        "phase100_bundle_dependency_ready": _phase100_dependency_ready(bundle_summary),
        "phase98_lifecycle_dependency_ready": _phase98_dependency_ready(lifecycle),
        "phase97_asgi_dependency_ready": _phase97_dependency_ready(phase97),
        "asgi_entrypoint_factory_ready": callable(app),
        "startup_plan_ready": _startup_plan_ready(startup_plan),
        "startup_command_preview_ready": _startup_command_preview_ready(startup_plan),
        "startup_command_preview_count": len(startup_plan["startup_command_preview"]),
        "startup_command_executed_count": 0,
        "readiness_probe_count": phase97["route_count"],
        "readiness_probe_pass_count": asgi_smoke["authenticated_asgi_smoke_pass_count"],
        "authenticated_probe_pass_count": asgi_smoke[
            "authenticated_asgi_smoke_pass_count"
        ],
        "unauthenticated_probe_rejected_count": asgi_smoke[
            "unauthenticated_asgi_smoke_rejected_count"
        ],
        "local_loopback_or_tailnet_only": _local_private_only(startup_plan),
        "bind_host_public_count": _bind_host_public_count(startup_plan),
        "env_placeholder_count": len(env_placeholders),
        "env_placeholder_missing_count": _missing_env_placeholder_count(
            env_placeholders,
            bundle,
        ),
        "secret_value_literal_count": _secret_value_literal_count(startup_plan),
        "rollback_step_count": len(rollback),
        "compose_service_count": bundle_summary["compose_service_count"],
        "host_port_publish_count": bundle_summary["host_port_publish_count"],
        "privileged_service_count": bundle_summary["privileged_service_count"],
        "host_bind_mount_count": bundle_summary["host_bind_mount_count"],
        "startup_plan": startup_plan,
        "readiness_probe_results": asgi_smoke,
        "rollback_steps": rollback,
        "trust_metadata": _trust_metadata(contract, bundle_summary),
        "container_manager_import_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_image_pull_attempt_count": 0,
        "container_start_attempt_count": 0,
        "uvicorn_run_attempt_count": 0,
        "network_bind_attempt_count": 0,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "point_in_time_claim_count": 0,
        "revised_mislabeled_as_pit_count": 0,
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
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        {
            "startup_plan": startup_plan,
            "rollback_steps": rollback,
            "trust_metadata": summary["trust_metadata"],
        },
    )
    summary["nas_private_local_startup_smoke_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_private_local_startup_smoke_ready"] else "blocked"
    )
    return summary


def summarize_nas_private_local_startup_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase101 private local startup smoke fields."""

    smoke = build_nas_private_local_startup_smoke(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_private_local_startup_smoke_contract_ready",
        "nas_private_local_startup_smoke_ready",
        "phase100_bundle_dependency_ready",
        "phase98_lifecycle_dependency_ready",
        "phase97_asgi_dependency_ready",
        "asgi_entrypoint_factory_ready",
        "startup_plan_ready",
        "startup_command_preview_ready",
        "startup_command_preview_count",
        "startup_command_executed_count",
        "readiness_probe_count",
        "readiness_probe_pass_count",
        "authenticated_probe_pass_count",
        "unauthenticated_probe_rejected_count",
        "local_loopback_or_tailnet_only",
        "bind_host_public_count",
        "env_placeholder_count",
        "env_placeholder_missing_count",
        "secret_value_literal_count",
        "rollback_step_count",
        "compose_service_count",
        "host_port_publish_count",
        "privileged_service_count",
        "host_bind_mount_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_image_pull_attempt_count",
        "container_start_attempt_count",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "point_in_time_claim_count",
        "revised_mislabeled_as_pit_count",
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
        "nas_private_local_startup_smoke": smoke,
    }


def write_nas_private_local_startup_smoke_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write startup smoke artifacts under an explicit temporary path."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase101 startup smoke output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    smoke = build_nas_private_local_startup_smoke(contract_path=contract_path)
    files = {
        "private-local-startup-plan.json": json.dumps(
            smoke["startup_plan"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "private-local-startup-smoke-report.json": json.dumps(
            {
                key: value
                for key, value in smoke.items()
                if key
                not in {
                    "startup_plan",
                    "readiness_probe_results",
                    "rollback_steps",
                    "trust_metadata",
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "private-local-startup-rollback.json": json.dumps(
            {"phase": 101, "rollback_steps": smoke["rollback_steps"]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
    }
    written = []
    for filename, content in files.items():
        path = output_path / filename
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return {
        "nas_private_local_startup_smoke_ready": smoke[
            "nas_private_local_startup_smoke_ready"
        ],
        "startup_smoke_output_path_count": len(written),
        "startup_smoke_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "written_paths": written,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if smoke["result"] == "passed" else "blocked",
    }


def _startup_plan(contract: dict[str, Any]) -> dict[str, Any]:
    scope = contract["startup_scope"]
    return {
        "phase": 101,
        "startup_command_preview": contract["startup_plan"][
            "startup_command_preview"
        ],
        "host": scope["local_loopback_host"],
        "port": scope["local_loopback_port"],
        "private_access_mode": scope["private_access_mode"],
        "asgi_factory": "business_cycle.service.nas_private_asgi_app:create_app",
        "command_preview_only": True,
        "uvicorn_run_allowed_now": False,
        "network_bind_allowed_now": False,
        "live_server_start_allowed_now": False,
        "required_environment_placeholders": contract["startup_plan"][
            "required_environment_placeholders"
        ],
        "readiness_probe_paths": contract["startup_plan"]["readiness_probe_paths"],
    }


def _rollback_steps(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": step,
            "ready": True,
            "live_resource_created_by_phase": False,
        }
        for step in contract["startup_plan"]["rollback_steps"]
    ]


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["startup_scope"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_device"] == "Synology DS925+"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["private_local_startup_smoke_allowed"] is True
        and scope["startup_command_preview_allowed"] is True
        and scope["asgi_factory_validation_allowed"] is True
        and scope["in_process_readiness_probe_allowed"] is True
        and scope["local_loopback_host"] == "127.0.0.1"
        and scope["uvicorn_run_allowed_now"] is False
        and scope["network_bind_allowed_now"] is False
        and scope["live_server_start_allowed_now"] is False
        and scope["container_manager_import_allowed_now"] is False
        and scope["docker_compose_execution_allowed_now"] is False
        and scope["container_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
    )


def _phase100_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_container_manager_bundle_ready"] is True
        and summary["compose_service_count"] == 3
        and summary["host_port_publish_count"] == 0
    )


def _phase98_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_service_lifecycle_ready"] is True
        and summary["readiness_probe_pass_count"] == summary["readiness_probe_count"]
        and summary["network_bind_attempt_count"] == 0
    )


def _phase97_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_asgi_adapter_ready"] is True
        and summary["local_asgi_smoke_ready"] is True
        and summary["uvicorn_run_attempt_count"] == 0
    )


def _startup_plan_ready(plan: dict[str, Any]) -> bool:
    return (
        plan["command_preview_only"] is True
        and plan["host"] == "127.0.0.1"
        and int(plan["port"]) == 8000
        and plan["uvicorn_run_allowed_now"] is False
        and plan["network_bind_allowed_now"] is False
        and plan["live_server_start_allowed_now"] is False
        and bool(plan["readiness_probe_paths"])
    )


def _startup_command_preview_ready(plan: dict[str, Any]) -> bool:
    commands = plan["startup_command_preview"]
    return (
        len(commands) == 1
        and "business_cycle.service.nas_private_asgi_app:create_app" in commands[0]
        and "--factory" in commands[0]
        and "--host 127.0.0.1" in commands[0]
    )


def _local_private_only(plan: dict[str, Any]) -> bool:
    return plan["host"] == "127.0.0.1" and plan["private_access_mode"] in {
        "loopback_or_tailscale_only",
        "tailscale_or_loopback_private_only",
    }


def _bind_host_public_count(plan: dict[str, Any]) -> int:
    public_hosts = {"0.0.0.0", "::", "public", "internet"}
    values = [str(plan["host"])] + [str(item) for item in plan["startup_command_preview"]]
    return sum(any(host in value for host in public_hosts) for value in values)


def _missing_env_placeholder_count(
    placeholders: list[str],
    bundle: dict[str, Any],
) -> int:
    text = json.dumps(
        {
            "compose": bundle["compose"],
            "env_template": bundle["env_template"],
        },
        sort_keys=True,
    )
    return sum(placeholder not in text for placeholder in placeholders)


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


def _trust_metadata(
    contract: dict[str, Any],
    bundle_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "nas_migration_surface": "private_local_startup_smoke",
        "target_device": contract["startup_scope"]["target_device"],
        "private_access_mode": contract["startup_scope"]["private_access_mode"],
        "source_bundle_phase": bundle_summary["phase"],
        "container_manager_import_attempted": False,
        "docker_compose_executed": False,
        "container_started": False,
        "uvicorn_run_attempted": False,
        "network_bound": False,
        "live_server_started": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
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
    expected.pop("nas_private_local_startup_smoke_ready", None)
    return expected
