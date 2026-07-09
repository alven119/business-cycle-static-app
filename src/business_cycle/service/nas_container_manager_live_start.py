"""Operator-owned Container Manager live start package for Phase 108.

This module prepares and validates the NAS live-start handoff after Phase 107
created a buildable app container bundle. It never logs in to DSM, imports a
Container Manager project, builds an image, starts containers, connects to
Postgres, or fetches live macro data. The operator performs those steps on the
NAS and may later provide a redacted report for validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_container_manager_live_start_contract.yaml"
PHASE107_CONTRACT_PATH = ROOT / "specs/common/nas_app_container_runtime_bundle_contract.yaml"
PHASE107_CLOSURE_PATH = (
    ROOT / "specs/audits/phase107_nas_app_container_runtime_bundle_closure.yaml"
)
PHASE106_CLOSURE_PATH = (
    ROOT / "specs/audits/phase106_nas_operator_live_deployment_session_closure.yaml"
)
TMP_ROOT = Path("/tmp")

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
    "secret_value",
    "password",
    "token",
}
SECRET_MARKERS = ("PASSWORD", "SECRET", "API_KEY", "TOKEN")


def load_nas_container_manager_live_start_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase108 live-start contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_container_manager_live_start_contract"])


def build_nas_container_manager_live_start_package(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    operator_report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a non-executing Phase108 live-start package."""

    contract = load_nas_container_manager_live_start_contract(contract_path)
    phase107 = _load_phase_closure_hard_gates(
        PHASE107_CLOSURE_PATH,
        "phase107_nas_app_container_runtime_bundle_closure",
    )
    phase106 = _load_phase_closure_hard_gates(
        PHASE106_CLOSURE_PATH,
        "phase106_nas_operator_live_deployment_session_closure",
    )
    action_register = _action_register(contract)
    report_template = _operator_report_template(contract, action_register)
    sample_report = _sample_operator_report(contract, action_register)
    actual_report = (
        _load_report(operator_report_path) if operator_report_path is not None else None
    )
    sample_validation = validate_nas_container_manager_live_start_report(
        sample_report,
        contract,
    )
    actual_validation = (
        validate_nas_container_manager_live_start_report(actual_report, contract)
        if actual_report is not None
        else _missing_report_validation(contract)
    )
    package_payload = {
        "action_register": action_register,
        "report_template": report_template,
        "sample_report": sample_report,
        "health_auth_smoke": _health_auth_smoke_checklist(contract),
        "rollback_drill": _rollback_drill_checklist(),
    }
    summary: dict[str, Any] = {
        "phase": "108",
        "phase_id": 108,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase108_nas_container_manager_live_start_package",
        "artifact_version": contract["version"],
        "output_mode": "operator_live_start_package_no_codex_execution",
        "research_only": True,
        "target_nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "target_device": contract["target_endpoint"]["target_device"],
        "package_runtime": contract["target_endpoint"]["package_runtime"],
        "access_model": contract["target_endpoint"]["access_model"],
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_container_manager_live_start_contract_ready": _contract_ready(contract),
        "phase107_runtime_bundle_dependency_ready": _phase107_ready(phase107),
        "phase106_operator_session_dependency_ready": _phase106_ready(phase106),
        "app_image_reference": contract["required_bundle"]["app_image_reference"],
        "expected_project_name": contract["required_bundle"]["expected_project_name"],
        "phase107_bundle_contract_hash": _hash_file(PHASE107_CONTRACT_PATH),
        "operator_stage_count": len(contract["operator_stages"]),
        "required_operator_action_count": len(action_register),
        "operator_action_with_manual_owner_count": sum(
            action["owner"] == "operator" for action in action_register
        ),
        "operator_action_auto_execution_count": sum(
            action["automatic_execution_allowed_now"] for action in action_register
        ),
        "operator_report_schema_ready": _report_schema_ready(contract),
        "operator_report_template_ready": _report_template_ready(
            report_template,
            contract,
        ),
        "sample_operator_live_start_report_valid": sample_validation[
            "operator_report_valid"
        ],
        "live_acceptance_requires_operator_report": bool(
            contract["live_start_scope"]["operator_report_required_for_live_acceptance"],
        ),
        "live_start_acceptance_status": actual_validation[
            "live_start_acceptance_status"
        ],
        "live_deployment_complete": actual_validation["live_deployment_complete"],
        "live_start_package_artifact_count": len(contract["required_package_artifacts"]),
        "package_output_under_tmp_only": True,
        "codex_dsm_login_attempt_count": 0,
        "codex_container_manager_import_attempt_count": 0,
        "codex_docker_build_attempt_count": 0,
        "codex_container_start_attempt_count": 0,
        "codex_live_server_start_attempt_count": 0,
        "codex_live_db_connection_attempt_count": 0,
        "codex_postgres_read_attempt_count": 0,
        "codex_postgres_write_attempt_count": 0,
        "codex_schema_migration_attempt_count": 0,
        "codex_live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "tests_network_dependency_count": 0,
        "private_access_required": True,
        "public_host_port_publish_count": 0,
        "refresh_worker_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "action_register": action_register,
        "operator_report_template": report_template,
        "sample_operator_report": sample_report,
        "operator_report_validation": actual_validation,
        "sample_operator_report_validation": sample_validation,
        "health_auth_smoke_checklist": package_payload["health_auth_smoke"],
        "rollback_drill_checklist": package_payload["rollback_drill"],
        "operator_next_steps": _operator_next_steps(contract),
        "project_import_notes": _project_import_notes(contract),
        "package_hash": _hash_payload(package_payload),
        "trust_metadata": _trust_metadata(contract),
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    summary["nas_container_manager_live_start_package_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed"
        if summary["nas_container_manager_live_start_package_ready"]
        else "blocked"
    )
    return summary


def summarize_nas_container_manager_live_start(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    operator_report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return compact Phase108 live-start package fields."""

    package = build_nas_container_manager_live_start_package(
        contract_path=contract_path,
        operator_report_path=operator_report_path,
    )
    keys = (
        "phase",
        "phase_id",
        "nas_container_manager_live_start_contract_ready",
        "nas_container_manager_live_start_package_ready",
        "phase107_runtime_bundle_dependency_ready",
        "phase106_operator_session_dependency_ready",
        "target_nas_private_ip",
        "app_image_reference",
        "expected_project_name",
        "operator_stage_count",
        "required_operator_action_count",
        "operator_action_with_manual_owner_count",
        "operator_action_auto_execution_count",
        "operator_report_schema_ready",
        "operator_report_template_ready",
        "sample_operator_live_start_report_valid",
        "live_acceptance_requires_operator_report",
        "live_start_acceptance_status",
        "live_deployment_complete",
        "live_start_package_artifact_count",
        "package_output_under_tmp_only",
        "codex_dsm_login_attempt_count",
        "codex_container_manager_import_attempt_count",
        "codex_docker_build_attempt_count",
        "codex_container_start_attempt_count",
        "codex_live_server_start_attempt_count",
        "codex_live_db_connection_attempt_count",
        "codex_postgres_read_attempt_count",
        "codex_postgres_write_attempt_count",
        "codex_schema_migration_attempt_count",
        "codex_live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "tests_network_dependency_count",
        "private_access_required",
        "public_host_port_publish_count",
        "refresh_worker_enabled",
        "label_used_by_runtime_count",
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
    return {key: package[key] for key in keys} | {
        "nas_container_manager_live_start_package": package,
    }


def validate_nas_container_manager_live_start_report(
    report: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an operator-supplied live-start report without executing it."""

    contract = contract or load_nas_container_manager_live_start_contract()
    required_fields = set(contract["operator_report_schema"]["required_top_level_fields"])
    allowed_statuses = set(contract["operator_report_schema"]["allowed_action_statuses"])
    expected_actions = {
        (action["stage_id"], action["action_id"]) for action in _action_register(contract)
    }
    actual_actions = {
        (stage["stage_id"], action["action_id"])
        for stage in report.get("stage_results", [])
        for action in stage.get("action_results", [])
    }
    statuses = [
        action.get("status")
        for stage in report.get("stage_results", [])
        for action in stage.get("action_results", [])
    ]
    health = dict(report.get("health_auth_summary", {}))
    rollback = dict(report.get("rollback_summary", {}))
    missing_fields = required_fields - set(report)
    missing_actions = expected_actions - actual_actions
    invalid_status_count = sum(status not in allowed_statuses for status in statuses)
    passed_action_count = sum(
        status == contract["operator_report_schema"]["passed_status"]
        for status in statuses
    )
    blocked = (
        bool(missing_fields)
        or bool(missing_actions)
        or invalid_status_count > 0
        or passed_action_count != len(expected_actions)
        or report.get("report_mode")
        != contract["operator_report_schema"]["report_mode"]
        or str(report.get("nas_private_ip"))
        != str(contract["target_endpoint"]["nas_private_ip"])
        or report.get("app_image_reference")
        != contract["required_bundle"]["app_image_reference"]
        or report.get("operator_attested") is not True
        or report.get("prohibited_live_outputs_absent") is not True
        or health.get("healthz_status") != "ok"
        or health.get("readyz_status") != "ready"
        or health.get("unauthenticated_dashboard_request") != "rejected"
        or health.get("authenticated_dashboard_request") != "allowed"
        or rollback.get("rollback_path_documented") is not True
        or rollback.get("volume_delete_required_for_rollback") is not False
        or _contains_prohibited_field(report) > 0
        or _secret_value_literal_count(report) > 0
    )
    return {
        "operator_report_valid": not blocked,
        "operator_report_action_count": len(actual_actions),
        "operator_report_passed_action_count": passed_action_count,
        "operator_report_missing_action_count": len(missing_actions),
        "operator_report_missing_field_count": len(missing_fields),
        "operator_report_invalid_status_count": invalid_status_count,
        "operator_report_prohibited_field_count": _contains_prohibited_field(report),
        "operator_report_secret_value_literal_count": _secret_value_literal_count(report),
        "live_start_acceptance_status": "accepted" if not blocked else "blocked",
        "live_deployment_complete": not blocked,
    }


def write_nas_container_manager_live_start_package(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write Phase108 live-start package artifacts under /tmp."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase108 NAS live-start package output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    package = build_nas_container_manager_live_start_package(
        contract_path=contract_path,
    )
    files = _package_files(package)
    written = []
    for filename, content in files.items():
        path = output_path / filename
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return {
        "nas_container_manager_live_start_package_ready": package[
            "nas_container_manager_live_start_package_ready"
        ],
        "live_start_package_output_path_count": len(written),
        "live_start_package_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "written_paths": written,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if package["result"] == "passed" else "blocked",
    }


def _action_register(contract: dict[str, Any]) -> list[dict[str, Any]]:
    actions = []
    for stage in contract["operator_stages"]:
        for index, action_id in enumerate(stage["required_action_ids"], start=1):
            actions.append(
                {
                    "stage_id": stage["stage_id"],
                    "action_id": action_id,
                    "sequence": index,
                    "owner": "operator",
                    "automatic_execution_allowed_now": False,
                    "codex_execution_attempted": False,
                },
            )
    return actions


def _operator_report_template(
    contract: dict[str, Any],
    action_register: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "session_id": "phase108-operator-live-start-YYYYMMDD",
        "report_mode": contract["operator_report_schema"]["report_mode"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "app_image_reference": contract["required_bundle"]["app_image_reference"],
        "operator_attested": False,
        "stage_results": _stage_results(action_register, status="not_run"),
        "health_auth_summary": {
            "healthz_status": "not_run",
            "readyz_status": "not_run",
            "unauthenticated_dashboard_request": "not_run",
            "authenticated_dashboard_request": "not_run",
            "private_access_path": "tailnet_or_private_lan_required",
        },
        "rollback_summary": {
            "rollback_path_documented": False,
            "volume_delete_required_for_rollback": False,
        },
        "prohibited_live_outputs_absent": False,
        "redaction_note": "Do not paste credentials, DSM account data, or API keys.",
    }


def _sample_operator_report(
    contract: dict[str, Any],
    action_register: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "session_id": "phase108-sample-accepted-report",
        "report_mode": contract["operator_report_schema"]["report_mode"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "app_image_reference": contract["required_bundle"]["app_image_reference"],
        "operator_attested": True,
        "stage_results": _stage_results(action_register, status="passed"),
        "health_auth_summary": {
            "healthz_status": "ok",
            "readyz_status": "ready",
            "unauthenticated_dashboard_request": "rejected",
            "authenticated_dashboard_request": "allowed",
            "private_access_path": "tailnet_or_private_lan_required",
        },
        "rollback_summary": {
            "rollback_path_documented": True,
            "volume_delete_required_for_rollback": False,
        },
        "prohibited_live_outputs_absent": True,
        "redaction_note": "Sample contains no credentials or secret values.",
    }


def _stage_results(
    action_register: list[dict[str, Any]],
    *,
    status: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for action in action_register:
        grouped.setdefault(action["stage_id"], []).append(
            {
                "action_id": action["action_id"],
                "status": status,
                "operator_note": "redacted",
            },
        )
    return [
        {"stage_id": stage_id, "action_results": action_results}
        for stage_id, action_results in grouped.items()
    ]


def _health_auth_smoke_checklist(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": 108,
        "private_access_required": True,
        "checks": [
            "Open the app through the private LAN or tailnet path only.",
            "Confirm /healthz returns ok.",
            "Confirm /readyz returns ready after dependencies are healthy.",
            "Confirm a request without the configured session header is rejected.",
            "Confirm a request with the configured session header renders the dashboard shell.",
            "Confirm the browser never receives database connection settings.",
        ],
        "target_image": contract["required_bundle"]["app_image_reference"],
    }


def _rollback_drill_checklist() -> dict[str, Any]:
    return {
        "phase": 108,
        "rollback_ready": True,
        "checks": [
            "Stop business_cycle_app first.",
            "Leave macro_postgres volume intact.",
            "Disable the project rather than deleting volumes.",
            "Record the image tag before any replacement.",
            "Keep rollback notes outside Git and without secret values.",
        ],
    }


def _operator_next_steps(contract: dict[str, Any]) -> str:
    image = contract["required_bundle"]["app_image_reference"]
    return "\n".join(
        [
            "# Phase108 operator next steps",
            "",
            "1. In DSM Container Manager, create/import the `business-cycle-research` project.",
            "2. Use the Phase107 compose bundle and build context under `/docker/business-cycle/app`.",
            f"3. Build the app image as `{image}`.",
            "4. Start Postgres, wait for healthy, then start the app service.",
            "5. Keep the refresh worker profile disabled.",
            "6. Run `/healthz`, `/readyz`, unauthenticated, and authenticated smoke checks.",
            "7. Fill `operator-live-start-report-template.json` without secrets.",
            "8. Send the redacted report back for validation before daily use.",
            "",
        ],
    )


def _project_import_notes(contract: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Container Manager import notes",
            "",
            f"- Target NAS: `{contract['target_endpoint']['nas_private_ip']}`",
            "- Project name: `business-cycle-research`",
            "- Host exposure remains private; do not add a public host port.",
            "- The app service uses loopback/private reverse-proxy handoff.",
            "- Keep environment values in DSM Container Manager, not Git.",
            "- Do not enable the refresh worker until a later live-refresh phase.",
            "",
        ],
    )


def _package_files(package: dict[str, Any]) -> dict[str, str]:
    return {
        "container-manager-live-start-checklist.md": _checklist_markdown(package),
        "operator-live-start-report-template.json": json.dumps(
            package["operator_report_template"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "sample-accepted-live-start-report.json": json.dumps(
            package["sample_operator_report"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "private-health-auth-smoke-checklist.md": _dict_markdown(
            "Private health/auth smoke checklist",
            package["health_auth_smoke_checklist"],
        ),
        "rollback-drill-checklist.md": _dict_markdown(
            "Rollback drill checklist",
            package["rollback_drill_checklist"],
        ),
        "phase108-operator-next-steps.md": package["operator_next_steps"],
        "container-manager-project-import-notes.md": package["project_import_notes"],
    }


def _checklist_markdown(package: dict[str, Any]) -> str:
    lines = [
        "# Phase108 Container Manager live-start checklist",
        "",
        f"- Target NAS: `{package['target_nas_private_ip']}`",
        f"- App image: `{package['app_image_reference']}`",
        f"- Expected project: `{package['expected_project_name']}`",
        "- Operator performs live actions; Codex does not execute DSM or Docker.",
        "",
    ]
    for stage in package["operator_report_template"]["stage_results"]:
        lines.append(f"## {stage['stage_id']}")
        for action in stage["action_results"]:
            lines.append(f"- [ ] {action['action_id']}")
        lines.append("")
    return "\n".join(lines)


def _dict_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", ""]
    for key, value in payload.items():
        if isinstance(value, list):
            lines.append(f"## {key}")
            lines.extend(f"- {item}" for item in value)
        else:
            lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["live_start_scope"]
    target = contract["target_endpoint"]
    return (
        contract["status"] == "active_operator_start_contract"
        and target["nas_private_ip"] == "192.168.1.116"
        and target["public_internet_exposure_allowed_now"] is False
        and scope["operator_owned_container_manager_import_allowed"] is True
        and scope["operator_owned_docker_build_allowed"] is True
        and scope["operator_owned_container_start_allowed"] is True
        and scope["operator_report_required_for_live_acceptance"] is True
        and scope["codex_dsm_login_allowed_now"] is False
        and scope["codex_container_manager_import_allowed_now"] is False
        and scope["codex_container_start_allowed_now"] is False
        and scope["codex_live_db_connection_allowed_now"] is False
        and scope["codex_postgres_write_allowed_now"] is False
        and scope["codex_live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["tests_network_dependency_allowed"] is False
    )


def _phase107_ready(hard_gates: dict[str, Any]) -> bool:
    return (
        hard_gates["nas_app_container_runtime_bundle_ready"] is True
        and hard_gates["app_image_reference"] == "business-cycle-nas-app:phase107"
        and hard_gates["container_start_attempt_count"] == 0
        and hard_gates["live_db_connection_attempt_count"] == 0
    )


def _phase106_ready(hard_gates: dict[str, Any]) -> bool:
    return (
        hard_gates["nas_operator_live_session_protocol_ready"] is True
        and hard_gates["operator_report_template_ready"] is True
        and hard_gates["live_deployment_complete"] is False
    )


def _report_schema_ready(contract: dict[str, Any]) -> bool:
    schema = contract["operator_report_schema"]
    return (
        schema["report_mode"] == "operator_attested_container_manager_live_start"
        and "stage_results" in schema["required_top_level_fields"]
        and schema["passed_status"] == "passed"
    )


def _report_template_ready(
    template: dict[str, Any],
    contract: dict[str, Any],
) -> bool:
    return (
        template["report_mode"] == contract["operator_report_schema"]["report_mode"]
        and template["nas_private_ip"] == str(contract["target_endpoint"]["nas_private_ip"])
        and template["app_image_reference"]
        == contract["required_bundle"]["app_image_reference"]
        and template["operator_attested"] is False
    )


def _missing_report_validation(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "operator_report_valid": False,
        "operator_report_action_count": 0,
        "operator_report_passed_action_count": 0,
        "operator_report_missing_action_count": len(_action_register(contract)),
        "operator_report_missing_field_count": len(
            contract["operator_report_schema"]["required_top_level_fields"],
        ),
        "operator_report_invalid_status_count": 0,
        "operator_report_prohibited_field_count": 0,
        "operator_report_secret_value_literal_count": 0,
        "live_start_acceptance_status": contract["operator_report_schema"][
            "missing_report_status"
        ],
        "live_deployment_complete": False,
    }


def _load_report(path: str | Path) -> dict[str, Any]:
    return dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _load_phase_closure_hard_gates(path: Path, key: str) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(payload[key]["hard_gates"])


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_container_manager_live_start_package_ready", None)
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


def _secret_value_literal_count(value: Any) -> int:
    if isinstance(value, dict):
        count = 0
        for key, item in value.items():
            key_has_marker = any(marker in str(key).upper() for marker in SECRET_MARKERS)
            value_is_literal = isinstance(item, str) and item not in {
                "",
                "redacted",
                "not_run",
            }
            count += int(key_has_marker and value_is_literal)
            count += _secret_value_literal_count(item)
        return count
    if isinstance(value, list):
        return sum(_secret_value_literal_count(item) for item in value)
    return 0


def _trust_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "nas_migration_surface": "container_manager_live_start_package",
        "target_device": contract["target_endpoint"]["target_device"],
        "app_image_reference": contract["required_bundle"]["app_image_reference"],
        "operator_report_required": True,
        "codex_live_execution_attempted": False,
        "public_exposure_allowed": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    return _hash_text(path.read_text(encoding="utf-8"))


def _hash_payload(payload: dict[str, Any]) -> str:
    return _hash_text(json.dumps(payload, sort_keys=True, ensure_ascii=True))


def _is_under_tmp(path: Path) -> bool:
    try:
        return path.resolve().is_relative_to(TMP_ROOT.resolve())
    except FileNotFoundError:
        return path.parent.resolve().is_relative_to(TMP_ROOT.resolve())
