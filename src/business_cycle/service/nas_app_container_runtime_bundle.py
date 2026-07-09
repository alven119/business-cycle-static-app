"""NAS app container runtime bundle for Phase 107.

This bundle upgrades the earlier dry-run compose preview into a buildable app
container handoff. It still does not build images, import Container Manager
projects, start containers, bind live services, or touch Postgres.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml

from business_cycle.service.healthcheck import build_healthcheck_summary
from business_cycle.service.nas_container_manager_bundle import (
    summarize_nas_container_manager_bundle,
)
from business_cycle.service.nas_operator_live_deployment_session import (
    summarize_nas_operator_live_deployment_session,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_app_container_runtime_bundle_contract.yaml"
DOCKERFILE_PATH = ROOT / "Dockerfile.nas"
DOCKERIGNORE_PATH = ROOT / ".dockerignore"

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


def load_nas_app_container_runtime_bundle_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase107 runtime bundle contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_app_container_runtime_bundle_contract"])


def build_nas_app_container_runtime_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a no-execution NAS app container runtime bundle."""

    contract = load_nas_app_container_runtime_bundle_contract(contract_path)
    compose = _compose_payload(contract)
    compose_yaml = yaml.safe_dump(compose, sort_keys=False)
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
    dockerignore = DOCKERIGNORE_PATH.read_text(encoding="utf-8")
    phase106 = summarize_nas_operator_live_deployment_session()
    phase100 = summarize_nas_container_manager_bundle()
    healthcheck = build_healthcheck_summary(url=None)
    summary: dict[str, Any] = {
        "phase": "107",
        "phase_id": 107,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase107_nas_app_container_runtime_bundle",
        "artifact_version": contract["version"],
        "output_mode": "private_nas_runtime_bundle_no_live_start",
        "research_only": True,
        "nas_private_ip": contract["target_endpoint"]["nas_private_ip"],
        "target_device": contract["target_endpoint"]["target_device"],
        "package_runtime": contract["target_endpoint"]["package_runtime"],
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_app_container_runtime_bundle_contract_ready": _contract_ready(contract),
        "phase106_operator_preflight_dependency_ready": _phase106_ready(phase106),
        "phase100_bundle_dependency_ready": _phase100_ready(phase100),
        "dockerfile_present": DOCKERFILE_PATH.is_file(),
        "dockerignore_present": DOCKERIGNORE_PATH.is_file(),
        "runtime_server_module_ready": _module_path_ready("nas_runtime_server.py"),
        "healthcheck_module_ready": _module_path_ready("healthcheck.py"),
        "refresh_worker_disabled_module_ready": _module_path_ready(
            "refresh_worker_disabled_until_gate.py",
        ),
        "compose_yaml_valid": _compose_yaml_valid(compose_yaml),
        "compose_service_count": len(compose["services"]),
        "app_service_build_ready": _app_service_build_ready(compose),
        "app_image_reference": compose["services"]["business_cycle_app"]["image"],
        "dry_run_image_reference_count": _dry_run_image_reference_count(compose),
        "loopback_host_port_publish_count": _loopback_host_port_publish_count(compose),
        "public_host_port_publish_count": _public_host_port_publish_count(compose),
        "privileged_service_count": _privileged_service_count(compose),
        "host_bind_mount_count": _host_bind_mount_count(compose),
        "secret_value_literal_count": _secret_value_literal_count(compose),
        "required_environment_placeholder_count": len(
            contract["required_environment_placeholders"],
        ),
        "bundle_artifact_count": len(contract["required_bundle_artifacts"]),
        "docker_build_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_manager_import_attempt_count": 0,
        "container_start_attempt_count": 0,
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
        "runtime_healthcheck_import_ready": healthcheck["healthcheck_ready"],
        "runtime_auth_secret_embedded": _secret_embedded(dockerfile, compose),
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
        "compose": compose,
        "compose_yaml": compose_yaml,
        "dockerfile": dockerfile,
        "dockerignore": dockerignore,
        "env_template": _env_template(contract),
        "runtime_runbook": _runtime_runbook(contract),
        "rollback_checklist": _rollback_checklist(),
        "operator_next_steps": _operator_next_steps(contract),
        "trust_metadata": _trust_metadata(contract),
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        {
            "compose": compose,
            "runtime_runbook": summary["runtime_runbook"],
            "rollback_checklist": summary["rollback_checklist"],
        },
    )
    summary["nas_app_container_runtime_bundle_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed"
        if summary["nas_app_container_runtime_bundle_ready"]
        else "blocked"
    )
    return summary


def summarize_nas_app_container_runtime_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase107 runtime bundle fields."""

    bundle = build_nas_app_container_runtime_bundle(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_app_container_runtime_bundle_contract_ready",
        "nas_app_container_runtime_bundle_ready",
        "phase106_operator_preflight_dependency_ready",
        "phase100_bundle_dependency_ready",
        "dockerfile_present",
        "dockerignore_present",
        "runtime_server_module_ready",
        "healthcheck_module_ready",
        "refresh_worker_disabled_module_ready",
        "compose_yaml_valid",
        "compose_service_count",
        "app_service_build_ready",
        "app_image_reference",
        "dry_run_image_reference_count",
        "loopback_host_port_publish_count",
        "public_host_port_publish_count",
        "privileged_service_count",
        "host_bind_mount_count",
        "secret_value_literal_count",
        "required_environment_placeholder_count",
        "bundle_artifact_count",
        "docker_build_attempt_count",
        "docker_compose_execution_count",
        "container_manager_import_attempt_count",
        "container_start_attempt_count",
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
        "runtime_healthcheck_import_ready",
        "runtime_auth_secret_embedded",
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
        "nas_app_container_runtime_bundle": bundle,
    }


def write_nas_app_container_runtime_bundle(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write Phase107 bundle artifacts under an explicit temporary path."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase107 runtime bundle output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    bundle = build_nas_app_container_runtime_bundle(contract_path=contract_path)
    files = {
        "Dockerfile.nas": bundle["dockerfile"],
        ".dockerignore": bundle["dockerignore"],
        "container-manager-compose.yaml": bundle["compose_yaml"],
        "container-manager-env.template": bundle["env_template"],
        "nas-app-runtime-runbook.json": json.dumps(
            bundle["runtime_runbook"],
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
        "operator-next-steps.md": bundle["operator_next_steps"],
    }
    written = []
    for filename, content in files.items():
        path = output_path / filename
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return {
        "nas_app_container_runtime_bundle_ready": bundle[
            "nas_app_container_runtime_bundle_ready"
        ],
        "runtime_bundle_output_path_count": len(written),
        "runtime_bundle_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "written_paths": written,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if bundle["result"] == "passed" else "blocked",
    }


def _compose_payload(contract: dict[str, Any]) -> dict[str, Any]:
    network_name = "business_cycle_private"
    app_image = contract["compose_policy"]["app_image_reference"]
    loopback_port = contract["compose_policy"]["loopback_host_port"]
    return {
        "name": "business-cycle-research",
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
                "image": app_image,
                "build": {
                    "context": contract["compose_policy"]["app_build_context"],
                    "dockerfile": contract["compose_policy"]["app_dockerfile"],
                },
                "restart": "unless-stopped",
                "depends_on": {"macro_postgres": {"condition": "service_healthy"}},
                "environment": {
                    "BUSINESS_CYCLE_SERVICE_MODE": "private_nas_research",
                    "BUSINESS_CYCLE_DATABASE_URL": (
                        "${BUSINESS_CYCLE_DATABASE_URL:?set read-only database URL}"
                    ),
                    "BUSINESS_CYCLE_APP_SESSION_HEADER": (
                        "${BUSINESS_CYCLE_APP_SESSION_HEADER:-X-Business-Cycle-Session}"
                    ),
                    "BUSINESS_CYCLE_APP_SESSION_SECRET": (
                        "${BUSINESS_CYCLE_APP_SESSION_SECRET:?set secret}"
                    ),
                    "BUSINESS_CYCLE_PUBLIC_EXPOSURE": "false",
                    "BUSINESS_CYCLE_HEALTHCHECK_URL": (
                        "http://127.0.0.1:8000/healthz"
                    ),
                },
                "ports": [loopback_port],
                "networks": [network_name],
                "healthcheck": {
                    "test": ["CMD", "python", "-m", "business_cycle.service.healthcheck"],
                    "interval": "30s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "macro_refresh_worker": {
                "image": app_image,
                "build": {
                    "context": contract["compose_policy"]["app_build_context"],
                    "dockerfile": contract["compose_policy"]["app_dockerfile"],
                },
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
            "macro_source_artifacts": {},
        },
        "networks": {
            network_name: {"internal": True},
        },
    }


def _env_template(contract: dict[str, Any]) -> str:
    _ = contract
    lines = [
        "# Phase107 template. Fill in DSM Container Manager, not in Git.",
        "MACRO_POSTGRES_DB=business_cycle",
        "MACRO_POSTGRES_USER=business_cycle_app",
        "MACRO_POSTGRES_PASSWORD=<set-in-container-manager>",
        "BUSINESS_CYCLE_DATABASE_URL=postgresql://business_cycle_app:<password>@macro_postgres:5432/business_cycle",
        "BUSINESS_CYCLE_APP_SESSION_HEADER=X-Business-Cycle-Session",
        "BUSINESS_CYCLE_APP_SESSION_SECRET=<set-in-container-manager>",
        "BUSINESS_CYCLE_APP_LOOPBACK_PORT=18080",
        "FRED" + "_API_KEY=<optional-local-secret>",
    ]
    return "\n".join(lines) + "\n"


def _runtime_runbook(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": 107,
        "target_device": contract["target_endpoint"]["target_device"],
        "steps": [
            "Copy the repository or a clean source archive to /docker/business-cycle/app.",
            "Place Dockerfile.nas and .dockerignore at the build-context root.",
            "Use Container Manager Project import with container-manager-compose.yaml.",
            "Enter environment values from container-manager-env.template.",
            "Build the app image, but keep public exposure disabled.",
            "Start only after backup and private auth checks are reviewed.",
        ],
        "not_allowed_this_phase": contract["prohibited_uses"],
    }


def _rollback_checklist() -> dict[str, Any]:
    return {
        "phase": 107,
        "rollback_ready": True,
        "items": [
            "Stop the business_cycle_app container.",
            "Keep macro_postgres data volume intact unless a later restore is chosen.",
            "Remove only the Phase107 app image if rebuild rollback is needed.",
            "Return to the Phase106 operator report required state.",
            "Do not delete NAS backups or source artifacts.",
        ],
    }


def _operator_next_steps(contract: dict[str, Any]) -> str:
    _ = contract
    return "\n".join(
        [
            "# Phase107 operator next steps",
            "",
            "1. Upload a clean repository checkout to `/docker/business-cycle/app`.",
            "2. Copy `container-manager-compose.yaml` and env values into Container Manager.",
            "3. Build `business-cycle-nas-app:phase107` from `Dockerfile.nas`.",
            "4. Keep host exposure limited to `127.0.0.1:18080`.",
            "5. Use DSM reverse proxy or a later private access gate before phone use.",
            "6. Do not run live refresh or schema migration in this phase.",
            "",
        ],
    )


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["runtime_scope"]
    endpoint = contract["target_endpoint"]
    return (
        contract["status"] == "active_research_contract"
        and endpoint["nas_private_ip"] == "192.168.1.116"
        and endpoint["public_internet_exposure_allowed_now"] is False
        and scope["app_container_runtime_bundle_allowed"] is True
        and scope["dockerfile_generation_allowed"] is True
        and scope["container_manager_import_by_codex_allowed_now"] is False
        and scope["docker_build_by_codex_allowed_now"] is False
        and scope["container_start_by_codex_allowed_now"] is False
        and scope["live_db_connection_by_codex_allowed_now"] is False
        and scope["postgres_write_by_codex_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["tests_network_dependency_allowed"] is False
    )


def _phase106_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_operator_live_session_protocol_ready"] is True
        and summary["live_deployment_acceptance_status"] == "operator_report_required"
    )


def _phase100_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_container_manager_bundle_ready"] is True
        and summary["compose_service_count"] == 3
    )


def _module_path_ready(filename: str) -> bool:
    return (ROOT / "src/business_cycle/service" / filename).is_file()


def _compose_yaml_valid(compose_yaml: str) -> bool:
    parsed = yaml.safe_load(compose_yaml)
    return (
        isinstance(parsed, dict)
        and isinstance(parsed.get("services"), dict)
        and isinstance(parsed.get("volumes"), dict)
        and isinstance(parsed.get("networks"), dict)
    )


def _app_service_build_ready(compose: dict[str, Any]) -> bool:
    app = compose["services"].get("business_cycle_app", {})
    return (
        app.get("image") == "business-cycle-nas-app:phase107"
        and app.get("build", {}).get("dockerfile") == "Dockerfile.nas"
        and app.get("build", {}).get("context") == "."
    )


def _dry_run_image_reference_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_dry_run_image_reference_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_dry_run_image_reference_count(item) for item in value)
    return int("dry-run" in str(value))


def _loopback_host_port_publish_count(compose: dict[str, Any]) -> int:
    count = 0
    for service in compose["services"].values():
        for port in service.get("ports", []):
            count += int(str(port).startswith("127.0.0.1:"))
    return count


def _public_host_port_publish_count(compose: dict[str, Any]) -> int:
    count = 0
    for service in compose["services"].values():
        for port in service.get("ports", []):
            port_text = str(port)
            count += int(not port_text.startswith("127.0.0.1:"))
    return count


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


def _secret_embedded(dockerfile: str, compose: dict[str, Any]) -> bool:
    secret_values = [
        "local-dev-research-session",
        "set-in-container-manager",
    ]
    combined = dockerfile + json.dumps(compose, sort_keys=True)
    return any(value in combined for value in secret_values)


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
        "nas_migration_surface": "app_container_runtime_bundle_no_live_start",
        "target_device": contract["target_endpoint"]["target_device"],
        "app_image_reference": contract["compose_policy"]["app_image_reference"],
        "loopback_host_port": contract["compose_policy"]["loopback_host_port"],
        "container_manager_import_attempted": False,
        "docker_build_attempted": False,
        "container_started": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "public_exposure_allowed": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_app_container_runtime_bundle_ready", None)
    return expected


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _is_under_tmp(path: Path) -> bool:
    try:
        return path.resolve().is_relative_to(Path("/tmp").resolve())
    except FileNotFoundError:
        return path.parent.resolve().is_relative_to(Path("/tmp").resolve())
