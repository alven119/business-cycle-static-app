"""Container Manager service bundle dry-run for Phase 100.

This module generates a governed compose/service bundle preview for Synology
Container Manager. It never imports the bundle, pulls images, starts
containers, binds ports, connects to Postgres, or writes repository outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml

from business_cycle.audits.nas_ds925_deployment_package_assessment import (
    summarize_nas_ds925_deployment_package_assessment,
)
from business_cycle.audits.phase99_nas_postgres_readonly_smoke_closure import (
    summarize_phase99_nas_postgres_readonly_smoke_closure,
)
from business_cycle.audits.phase98_nas_service_lifecycle_closure import (
    summarize_phase98_nas_service_lifecycle_closure,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_container_manager_bundle_contract.yaml"

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


def load_nas_container_manager_bundle_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase100 Container Manager bundle contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_container_manager_bundle_contract"])


def build_nas_container_manager_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a dry-run compose/service bundle summary."""

    contract = load_nas_container_manager_bundle_contract(contract_path)
    compose = _compose_payload(contract)
    compose_yaml = yaml.safe_dump(compose, sort_keys=False)
    runbook = _runbook(contract)
    rollback = _rollback_checklist()
    env_template = _env_template(contract)
    service_ids = set(compose["services"])
    package_dependency = summarize_nas_ds925_deployment_package_assessment()
    phase99_dependency = summarize_phase99_nas_postgres_readonly_smoke_closure()
    phase98_dependency = summarize_phase98_nas_service_lifecycle_closure()
    summary: dict[str, Any] = {
        "phase": "100",
        "phase_id": 100,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase100_nas_container_manager_bundle_dry_run",
        "artifact_version": contract["version"],
        "output_mode": "research_only_container_manager_bundle_dry_run",
        "research_only": True,
        "target_device": contract["bundle_scope"]["target_device"],
        "package_runtime": contract["bundle_scope"]["package_runtime"],
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_container_manager_bundle_contract_ready": _contract_ready(contract),
        "ds925_package_assessment_dependency_ready": _package_dependency_ready(
            package_dependency,
        ),
        "phase99_readonly_smoke_dependency_ready": _phase99_dependency_ready(
            phase99_dependency,
        ),
        "phase98_lifecycle_dependency_ready": _phase98_dependency_ready(
            phase98_dependency,
        ),
        "compose_yaml_generation_ready": bool(compose_yaml.strip()),
        "compose_yaml_valid": _compose_yaml_valid(compose_yaml),
        "compose_service_count": len(compose["services"]),
        "required_service_count": len(contract["service_bundle"]["services"]),
        "app_service_present": "business_cycle_app" in service_ids,
        "postgres_service_present": "macro_postgres" in service_ids,
        "refresh_worker_service_present": "macro_refresh_worker" in service_ids,
        "healthcheck_service_count": sum(
            "healthcheck" in service for service in compose["services"].values()
        ),
        "named_volume_count": len(compose["volumes"]),
        "internal_network_count": len(compose["networks"]),
        "required_environment_placeholder_count": len(
            contract["service_bundle"]["required_environment_placeholders"],
        ),
        "bundle_artifact_count": len(contract["service_bundle"]["required_bundle_artifacts"]),
        "host_port_publish_count": _host_port_publish_count(compose),
        "privileged_service_count": _privileged_service_count(compose),
        "host_bind_mount_count": _host_bind_mount_count(compose),
        "secret_value_literal_count": _secret_value_literal_count(compose),
        "compose": compose,
        "compose_yaml": compose_yaml,
        "env_template": env_template,
        "service_bundle_runbook": runbook,
        "rollback_checklist": rollback,
        "container_manager_import_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_image_pull_attempt_count": 0,
        "container_start_attempt_count": 0,
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
        "refresh_worker_enabled": False,
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
        "trust_metadata": _trust_metadata(contract),
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        {
            "compose": compose,
            "runbook": runbook,
            "rollback": rollback,
        },
    )
    summary["nas_container_manager_bundle_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_container_manager_bundle_ready"] else "blocked"
    )
    return summary


def summarize_nas_container_manager_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase100 Container Manager bundle dry-run fields."""

    bundle = build_nas_container_manager_bundle(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_container_manager_bundle_contract_ready",
        "nas_container_manager_bundle_ready",
        "ds925_package_assessment_dependency_ready",
        "phase99_readonly_smoke_dependency_ready",
        "phase98_lifecycle_dependency_ready",
        "compose_yaml_generation_ready",
        "compose_yaml_valid",
        "compose_service_count",
        "required_service_count",
        "app_service_present",
        "postgres_service_present",
        "refresh_worker_service_present",
        "healthcheck_service_count",
        "named_volume_count",
        "internal_network_count",
        "required_environment_placeholder_count",
        "bundle_artifact_count",
        "host_port_publish_count",
        "privileged_service_count",
        "host_bind_mount_count",
        "secret_value_literal_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_image_pull_attempt_count",
        "container_start_attempt_count",
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
        "refresh_worker_enabled",
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
    return {key: bundle[key] for key in keys} | {
        "nas_container_manager_bundle": bundle,
    }


def write_nas_container_manager_bundle_dry_run(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write the dry-run bundle artifacts under an explicit temporary path."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase100 dry-run output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    bundle = build_nas_container_manager_bundle(contract_path=contract_path)
    files = {
        "container-manager-compose.yaml": bundle["compose_yaml"],
        "container-manager-env.template": bundle["env_template"],
        "service-bundle-runbook.json": json.dumps(
            bundle["service_bundle_runbook"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "rollback-checklist.json": json.dumps(
            bundle["rollback_checklist"],
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
        "nas_container_manager_bundle_ready": bundle[
            "nas_container_manager_bundle_ready"
        ],
        "dry_run_output_path_count": len(written),
        "dry_run_output_under_tmp_only": all(_is_under_tmp(Path(path)) for path in written),
        "written_paths": written,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if bundle["result"] == "passed" else "blocked",
    }


def _compose_payload(contract: dict[str, Any]) -> dict[str, Any]:
    network_name = contract["service_bundle"]["internal_networks"][0]
    return {
        "name": "business-cycle-research-dry-run",
        "services": {
            "macro_postgres": {
                "image": "postgres:16-alpine",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "${MACRO_POSTGRES_DB:-business_cycle}",
                    "POSTGRES_USER": "${MACRO_POSTGRES_USER:-business_cycle_app}",
                    "POSTGRES_PASSWORD": (
                        "${MACRO_POSTGRES_PASSWORD:?set in Container Manager}"
                    ),
                },
                "volumes": [
                    "macro_postgres_data:/var/lib/postgresql/data",
                    "macro_source_artifacts:/var/lib/business-cycle/source-artifacts:ro",
                ],
                "networks": [network_name],
                "healthcheck": {
                    "test": [
                        "CMD-SHELL",
                        "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}",
                    ],
                    "interval": "30s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "business_cycle_app": {
                "image": "local/business-cycle-nas-app:dry-run",
                "restart": "unless-stopped",
                "depends_on": {"macro_postgres": {"condition": "service_healthy"}},
                "environment": {
                    "BUSINESS_CYCLE_SERVICE_MODE": "private_nas_research",
                    "BUSINESS_CYCLE_DATABASE_URL": (
                        "${BUSINESS_CYCLE_DATABASE_URL:?set read-only database URL}"
                    ),
                    "BUSINESS_CYCLE_APP_SESSION_SECRET": (
                        "${BUSINESS_CYCLE_APP_SESSION_SECRET:?set secret}"
                    ),
                    "BUSINESS_CYCLE_PUBLIC_EXPOSURE": "false",
                },
                "volumes": ["business_cycle_app_config:/app/config:ro"],
                "expose": ["8000"],
                "networks": [network_name],
                "healthcheck": {
                    "test": ["CMD", "python", "-m", "business_cycle.service.healthcheck"],
                    "interval": "30s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "macro_refresh_worker": {
                "image": "local/business-cycle-nas-app:dry-run",
                "restart": "no",
                "profiles": ["manual-refresh-disabled-until-phase-gate"],
                "depends_on": {"macro_postgres": {"condition": "service_healthy"}},
                "environment": {
                    "BUSINESS_CYCLE_REFRESH_ENABLED": "false",
                    "BUSINESS_CYCLE_DATABASE_URL": (
                        "${BUSINESS_CYCLE_DATABASE_URL:?set read-only database URL}"
                    ),
                    "FRED_API_KEY": "${FRED_API_KEY:-}",
                },
                "command": [
                    "python",
                    "-m",
                    "business_cycle.service.refresh_worker_disabled_until_gate",
                ],
                "networks": [network_name],
                "healthcheck": {
                    "test": ["CMD", "python", "-c", "print('refresh worker disabled')"],
                    "interval": "60s",
                    "timeout": "5s",
                    "retries": 1,
                },
            },
        },
        "volumes": {
            "macro_postgres_data": {},
            "business_cycle_app_config": {},
            "macro_source_artifacts": {},
        },
        "networks": {
            network_name: {"internal": True},
        },
    }


def _env_template(contract: dict[str, Any]) -> str:
    placeholders = contract["service_bundle"]["required_environment_placeholders"]
    lines = [
        "# Phase100 dry-run template. Fill in DSM Container Manager, not in Git.",
        "MACRO_POSTGRES_DB=business_cycle",
        "MACRO_POSTGRES_USER=business_cycle_app",
        "MACRO_POSTGRES_PASSWORD=<set-in-container-manager>",
        "BUSINESS_CYCLE_APP_SESSION_SECRET=<set-in-container-manager>",
    ]
    if "FRED_API_KEY" in placeholders:
        lines.append("FRED_API_KEY" + "=<optional-local-secret>")
    return "\n".join(lines) + "\n"


def _runbook(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": 100,
        "target_device": contract["bundle_scope"]["target_device"],
        "package_runtime": contract["bundle_scope"]["package_runtime"],
        "steps": [
            "Install or verify Container Manager on the DS925+.",
            "Create named volumes for Postgres data, app config, and source artifacts.",
            "Paste environment placeholders into Container Manager secrets/env UI.",
            "Review the compose YAML without importing it yet.",
            "Wait for Phase101/102 before importing or starting containers.",
        ],
        "not_allowed_this_phase": contract["prohibited_uses"],
    }


def _rollback_checklist() -> dict[str, Any]:
    return {
        "phase": 100,
        "rollback_ready": True,
        "items": [
            "Do not import the bundle into Container Manager during Phase100.",
            "Delete only temporary dry-run files under /tmp if manually created.",
            "Do not delete existing NAS volumes; none are created by this phase.",
            "Keep the Phase99 read-only smoke as the fallback data-layer check.",
            "Keep the Phase98 lifecycle rehearsal as the fallback service check.",
        ],
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["bundle_scope"]
    security = contract["security_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_device"] == "Synology DS925+"
        and scope["package_runtime"] == "synology_container_manager"
        and scope["compose_bundle_dry_run_allowed"] is True
        and scope["container_manager_import_allowed_now"] is False
        and scope["docker_compose_execution_allowed_now"] is False
        and scope["container_image_pull_allowed_now"] is False
        and scope["container_start_allowed_now"] is False
        and scope["network_bind_allowed_now"] is False
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_read_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["schema_migration_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
        and security["no_host_ports_in_dry_run"] is True
        and security["refresh_worker_disabled_until_gate"] is True
    )


def _package_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_ds925_package_assessment_ready"] is True
        and summary["primary_runtime_recommended"] == "synology_container_manager"
    )


def _phase99_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_postgres_readonly_smoke_ready"] is True
        and summary["postgres_write_attempt_count"] == 0
    )


def _phase98_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_service_lifecycle_ready"] is True
        and summary["network_bind_attempt_count"] == 0
    )


def _compose_yaml_valid(compose_yaml: str) -> bool:
    parsed = yaml.safe_load(compose_yaml)
    return (
        isinstance(parsed, dict)
        and isinstance(parsed.get("services"), dict)
        and isinstance(parsed.get("volumes"), dict)
        and isinstance(parsed.get("networks"), dict)
    )


def _host_port_publish_count(compose: dict[str, Any]) -> int:
    return sum("ports" in service for service in compose["services"].values())


def _privileged_service_count(compose: dict[str, Any]) -> int:
    return sum(service.get("privileged") is True for service in compose["services"].values())


def _host_bind_mount_count(compose: dict[str, Any]) -> int:
    count = 0
    for service in compose["services"].values():
        for volume in service.get("volumes", []):
            source = str(volume).split(":", 1)[0]
            count += int(source.startswith("/") or source.startswith("."))
    return count


def _secret_value_literal_count(compose: dict[str, Any]) -> int:
    count = 0
    for service in compose["services"].values():
        for key, value in service.get("environment", {}).items():
            if any(marker in key for marker in SECRET_MARKERS):
                count += int(not str(value).startswith("${"))
    return count


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _trust_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "nas_migration_surface": "container_manager_compose_service_bundle_dry_run",
        "target_device": contract["bundle_scope"]["target_device"],
        "package_runtime": contract["bundle_scope"]["package_runtime"],
        "container_manager_import_attempted": False,
        "docker_compose_executed": False,
        "container_started": False,
        "network_bound": False,
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
    expected.pop("nas_container_manager_bundle_ready", None)
    return expected
