"""Operator-guided NAS live deployment session protocol for Phase 106.

This module prepares and validates the operator session artifacts needed for a
future DS925+ live deployment. It never logs in to DSM, imports Container
Manager bundles, starts containers, connects to Postgres, or writes repository
outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import ipaddress
import json

import yaml

from business_cycle.service.nas_operator_deployment_handoff import (
    summarize_nas_operator_deployment_handoff,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_operator_live_deployment_session_contract.yaml"
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


def load_nas_operator_live_deployment_session_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase106 operator live deployment session contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_operator_live_deployment_session_contract"])


def build_nas_operator_live_deployment_session(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    operator_report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a Phase106 session protocol summary without live side effects."""

    contract = load_nas_operator_live_deployment_session_contract(contract_path)
    handoff = summarize_nas_operator_deployment_handoff()
    action_register = _action_register(contract)
    report_template = _operator_report_template(contract, action_register)
    sample_report = _sample_operator_report(contract, action_register)
    actual_report = (
        _load_report(operator_report_path) if operator_report_path is not None else None
    )
    sample_validation = validate_operator_live_session_report(sample_report, contract)
    actual_validation = (
        validate_operator_live_session_report(actual_report, contract)
        if actual_report is not None
        else _missing_report_validation()
    )
    payload_for_scan = {
        "action_register": action_register,
        "report_template": report_template,
        "sample_report": sample_report,
        "acceptance_policy": contract["acceptance_policy"],
    }
    summary: dict[str, Any] = {
        "phase": "106",
        "phase_id": 106,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase106_nas_operator_live_deployment_session",
        "artifact_version": contract["version"],
        "output_mode": "research_only_operator_live_session_protocol",
        "research_only": True,
        "target_device": contract["target_endpoint"]["target_device"],
        "package_runtime": contract["target_endpoint"]["package_runtime"],
        "access_model": contract["target_endpoint"]["access_model"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "nas_private_ip_source": contract["target_endpoint"]["ip_source"],
        "nas_private_ip_private_lan": _is_private_lan_ip(
            str(contract["target_endpoint"]["nas_private_ip"]),
        ),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_operator_live_session_contract_ready": _contract_ready(contract),
        "nas_operator_live_session_protocol_ready": True,
        "phase105_handoff_dependency_ready": _phase105_dependency_ready(handoff),
        "operator_must_execute_live_steps_out_of_band": bool(
            contract["session_scope"]["operator_must_execute_live_steps_out_of_band"],
        ),
        "automatic_live_execution_allowed_now": bool(
            contract["session_scope"]["automatic_live_execution_allowed_now"],
        ),
        "session_stage_count": len(contract["session_stages"]),
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
        "sample_operator_report_valid": sample_validation["operator_report_valid"],
        "live_acceptance_requires_operator_report": bool(
            contract["acceptance_policy"]["operator_report_required_for_live_acceptance"],
        ),
        "live_deployment_acceptance_status": actual_validation[
            "live_deployment_acceptance_status"
        ],
        "live_deployment_complete": actual_validation["live_deployment_complete"],
        "session_artifact_count": len(
            _session_files({}, {"trust_metadata": {}}),
        ),
        "action_register": action_register,
        "operator_report_template": report_template,
        "sample_operator_report": sample_report,
        "operator_report_validation": actual_validation,
        "sample_operator_report_validation": sample_validation,
        "acceptance_policy": contract["acceptance_policy"],
        "session_hash": _hash_payload(payload_for_scan),
        "trust_metadata": _trust_metadata(contract, handoff),
        "dsm_login_attempt_count": 0,
        "package_install_attempt_count": 0,
        "tailnet_login_attempt_count": 0,
        "container_manager_import_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_start_attempt_count": 0,
        "live_server_start_attempt_count": 0,
        "network_bind_attempt_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "backup_command_execution_count": 0,
        "restore_command_execution_count": 0,
        "live_fetch_attempt_count": 0,
        "tests_network_dependency_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "secret_value_literal_count": _secret_value_literal_count(payload_for_scan),
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
        payload_for_scan,
    )
    summary["nas_operator_live_session_protocol_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_operator_live_session_protocol_ready"] else "blocked"
    )
    return summary


def summarize_nas_operator_live_deployment_session(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase106 session readiness fields."""

    session = build_nas_operator_live_deployment_session(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_operator_live_session_contract_ready",
        "nas_operator_live_session_protocol_ready",
        "phase105_handoff_dependency_ready",
        "nas_private_ip",
        "nas_private_ip_private_lan",
        "operator_must_execute_live_steps_out_of_band",
        "automatic_live_execution_allowed_now",
        "session_stage_count",
        "required_operator_action_count",
        "operator_action_with_manual_owner_count",
        "operator_action_auto_execution_count",
        "operator_report_schema_ready",
        "operator_report_template_ready",
        "sample_operator_report_valid",
        "live_acceptance_requires_operator_report",
        "live_deployment_acceptance_status",
        "live_deployment_complete",
        "session_artifact_count",
        "dsm_login_attempt_count",
        "package_install_attempt_count",
        "tailnet_login_attempt_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_start_attempt_count",
        "live_server_start_attempt_count",
        "network_bind_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "backup_command_execution_count",
        "restore_command_execution_count",
        "live_fetch_attempt_count",
        "tests_network_dependency_count",
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
    return {key: session[key] for key in keys} | {
        "nas_operator_live_deployment_session": session,
    }


def validate_operator_live_session_report(
    report: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an operator-supplied live-session report without executing it."""

    contract = contract or load_nas_operator_live_deployment_session_contract()
    required_fields = set(contract["report_schema"]["required_top_level_fields"])
    allowed_statuses = set(contract["report_schema"]["allowed_action_statuses"])
    expected_actions = {
        (action["stage_id"], action["action_id"])
        for action in _action_register(contract)
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
    missing_fields = required_fields - set(report)
    missing_actions = expected_actions - actual_actions
    invalid_status_count = sum(status not in allowed_statuses for status in statuses)
    passed_action_count = sum(status == contract["report_schema"]["passed_status"] for status in statuses)
    blocked = (
        bool(missing_fields)
        or bool(missing_actions)
        or invalid_status_count > 0
        or report.get("report_mode") != contract["report_schema"]["report_mode"]
        or str(report.get("nas_private_ip")) != str(contract["target_endpoint"]["nas_private_ip"])
        or report.get("operator_attested") is not True
        or report.get("prohibited_live_outputs_absent") is not True
        or _contains_prohibited_field(report) > 0
        or _secret_value_literal_count(report) > 0
        or passed_action_count != len(expected_actions)
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
        "live_deployment_acceptance_status": "accepted" if not blocked else "blocked",
        "live_deployment_complete": not blocked,
    }


def write_nas_operator_live_deployment_session_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write Phase106 live-session protocol artifacts under /tmp."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase106 NAS live session output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    session = build_nas_operator_live_deployment_session(contract_path=contract_path)
    files = _session_files(
        {
            "action_register": session["action_register"],
            "operator_report_template": session["operator_report_template"],
            "sample_operator_report": session["sample_operator_report"],
            "acceptance_policy": session["acceptance_policy"],
            "operator_report_validation": session["operator_report_validation"],
        },
        session,
    )
    written = []
    for filename, payload in files.items():
        path = output_path / filename
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(str(path))
    return {
        "nas_operator_live_session_protocol_ready": session[
            "nas_operator_live_session_protocol_ready"
        ],
        "session_output_path_count": len(written),
        "session_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "written_paths": written,
        "result": "passed",
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["session_scope"]
    target = contract["target_endpoint"]
    return (
        contract["status"] == "active_research_contract"
        and scope["default_mode"] == "operator_guided_live_session_protocol"
        and scope["operator_must_execute_live_steps_out_of_band"] is True
        and scope["automatic_live_execution_allowed_now"] is False
        and scope["dsm_login_by_codex_allowed_now"] is False
        and scope["container_manager_import_by_codex_allowed_now"] is False
        and scope["postgres_write_by_codex_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
        and target["private_lan_only"] is True
        and _is_private_lan_ip(str(target["nas_private_ip"]))
    )


def _phase105_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_operator_deployment_handoff_ready"] is True
        and summary["live_execution_allowed_now"] is False
    )


def _action_register(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sequence = 1
    for stage in contract["session_stages"]:
        for action_id in stage["required_action_ids"]:
            rows.append(
                {
                    "sequence": sequence,
                    "stage_id": stage["stage_id"],
                    "action_id": action_id,
                    "owner": "operator",
                    "automatic_execution_allowed_now": False,
                    "requires_out_of_band_action": True,
                    "required_status_for_acceptance": "passed",
                    "status": "pending_operator_execution",
                },
            )
            sequence += 1
    return rows


def _operator_report_template(
    contract: dict[str, Any],
    action_register: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "session_id": "phase106_ds925_operator_live_session",
        "report_mode": contract["report_schema"]["report_mode"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "operator_attested": False,
        "stage_results": _stage_results(action_register, status="not_run"),
        "prohibited_live_outputs_absent": True,
        "report_storage_policy": "operator_keeps_outside_repo_or_tmp_only",
    }


def _sample_operator_report(
    contract: dict[str, Any],
    action_register: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "session_id": "phase106_ds925_operator_live_session_sample",
        "report_mode": contract["report_schema"]["report_mode"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "operator_attested": True,
        "stage_results": _stage_results(action_register, status="passed"),
        "prohibited_live_outputs_absent": True,
        "report_storage_policy": "sample_for_schema_validation_only",
    }


def _stage_results(
    action_register: list[dict[str, Any]],
    *,
    status: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for action in action_register:
        grouped.setdefault(action["stage_id"], []).append(
            {
                "action_id": action["action_id"],
                "status": status,
                "evidence_reference": "operator_attestation_outside_repo",
            },
        )
    return [
        {"stage_id": stage_id, "action_results": actions}
        for stage_id, actions in grouped.items()
    ]


def _report_schema_ready(contract: dict[str, Any]) -> bool:
    required = set(contract["report_schema"]["required_top_level_fields"])
    return (
        {"session_id", "report_mode", "stage_results"} <= required
        and contract["report_schema"]["passed_status"]
        in contract["report_schema"]["allowed_action_statuses"]
    )


def _report_template_ready(template: dict[str, Any], contract: dict[str, Any]) -> bool:
    required = set(contract["report_schema"]["required_top_level_fields"])
    return required <= set(template) and template["operator_attested"] is False


def _missing_report_validation() -> dict[str, Any]:
    return {
        "operator_report_valid": False,
        "operator_report_action_count": 0,
        "operator_report_passed_action_count": 0,
        "operator_report_missing_action_count": 41,
        "operator_report_missing_field_count": 0,
        "operator_report_invalid_status_count": 0,
        "operator_report_prohibited_field_count": 0,
        "operator_report_secret_value_literal_count": 0,
        "live_deployment_acceptance_status": "operator_report_required",
        "live_deployment_complete": False,
    }


def _load_report(path: str | Path) -> dict[str, Any]:
    return dict(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def _session_files(payload: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    summary_payload = {
        key: value
        for key, value in session.items()
        if key
        not in {
            "action_register",
            "operator_report_template",
            "sample_operator_report",
            "operator_report_validation",
            "sample_operator_report_validation",
            "acceptance_policy",
            "trust_metadata",
        }
    }
    return {
        "ds925-live-session-action-register.json": payload.get("action_register", []),
        "ds925-live-session-report-template.json": payload.get(
            "operator_report_template",
            {},
        ),
        "ds925-live-session-sample-report.json": payload.get(
            "sample_operator_report",
            {},
        ),
        "ds925-live-session-acceptance-policy.json": payload.get(
            "acceptance_policy",
            {},
        ),
        "ds925-live-session-report-validation.json": payload.get(
            "operator_report_validation",
            {},
        ),
        "ds925-live-session-summary.json": summary_payload,
        "ds925-live-session-trust-metadata.json": session.get("trust_metadata", {}),
    }


def _trust_metadata(
    contract: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    return {
        "output_label": "research_only_private_nas_live_session_protocol",
        "target_endpoint": str(contract["target_endpoint"]["nas_private_ip"]),
        "private_lan_only": True,
        "operator_must_execute_live_steps_out_of_band": True,
        "automatic_live_execution_allowed_now": False,
        "phase105_handoff_ready": handoff["nas_operator_deployment_handoff_ready"],
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
        "portfolio_instruction_enabled": False,
        "public_output_enabled": False,
    }


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected_without_self = dict(expected)
    expected_without_self.pop("nas_operator_live_session_protocol_ready", None)
    return expected_without_self


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if str(key).lower() in PROHIBITED_FIELDS else 0)
            + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _secret_value_literal_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_secret_value_literal_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_secret_value_literal_count(item) for item in value)
    if isinstance(value, str):
        rendered = value.upper()
        return sum(marker in rendered for marker in SECRET_MARKERS)
    return 0


def _is_private_lan_ip(value: str) -> bool:
    return ipaddress.ip_address(value).is_private


def _is_under_tmp(path: Path) -> bool:
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    return resolved == tmp_resolved or tmp_resolved in resolved.parents
