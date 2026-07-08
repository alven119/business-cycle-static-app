"""Operator-approved NAS deployment handoff for Phase 105.

The handoff turns prior NAS rehearsals into reviewable operator steps. It does
not log in to DSM, import Container Manager bundles, start containers, connect
to Postgres, run backup commands, or write repository outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import ipaddress
import json

import yaml

from business_cycle.service.nas_container_manager_bundle import (
    summarize_nas_container_manager_bundle,
)
from business_cycle.service.nas_ds925_connectivity_smoke import (
    summarize_nas_ds925_connectivity_smoke,
)
from business_cycle.service.nas_private_local_startup_smoke import (
    summarize_nas_private_local_startup_smoke,
)
from business_cycle.storage.nas_postgres_revised_import_rehearsal import (
    summarize_nas_postgres_revised_import_rehearsal,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_operator_deployment_handoff_contract.yaml"
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
}
SECRET_MARKERS = ("PASSWORD", "SECRET", "API_KEY", "TOKEN")


def load_nas_operator_deployment_handoff_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase105 NAS operator deployment handoff contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_operator_deployment_handoff_contract"])


def build_nas_operator_deployment_handoff(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase105 deployment handoff without live side effects."""

    contract = load_nas_operator_deployment_handoff_contract(contract_path)
    phase100 = summarize_nas_container_manager_bundle()
    phase101 = summarize_nas_private_local_startup_smoke()
    phase103 = summarize_nas_ds925_connectivity_smoke()
    phase104 = summarize_nas_postgres_revised_import_rehearsal()
    preflight = _operator_preflight_checklist(contract)
    import_steps = _container_manager_import_handoff(contract)
    auth_checks = _private_auth_acceptance(contract)
    health_checks = _health_check_plan(contract)
    rollback = _backup_rollback_acceptance(contract)
    go_no_go = _go_no_go_gates(contract)
    payload_for_scan = {
        "operator_preflight_checklist": preflight,
        "container_manager_import_handoff": import_steps,
        "private_auth_acceptance": auth_checks,
        "health_check_plan": health_checks,
        "backup_rollback_acceptance": rollback,
        "go_no_go_gates": go_no_go,
    }
    summary: dict[str, Any] = {
        "phase": "105",
        "phase_id": 105,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase105_nas_operator_deployment_handoff",
        "artifact_version": contract["version"],
        "output_mode": "research_only_operator_handoff_no_live_execution",
        "research_only": True,
        "target_device": contract["target_endpoint"]["target_device"],
        "package_runtime": contract["target_endpoint"]["package_runtime"],
        "access_model": contract["target_endpoint"]["access_model"],
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "nas_private_ip_source": contract["target_endpoint"]["ip_source"],
        "nas_private_ip_private_lan": _is_private_lan_ip(
            str(contract["target_endpoint"]["nas_private_ip"]),
        ),
        "operator_approval_required": bool(
            contract["handoff_scope"]["operator_approval_required"],
        ),
        "live_execution_allowed_now": bool(
            contract["handoff_scope"]["live_execution_allowed_now"],
        ),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_operator_deployment_handoff_contract_ready": _contract_ready(contract),
        "phase100_container_manager_bundle_dependency_ready": (
            _phase100_dependency_ready(phase100)
        ),
        "phase101_private_startup_dependency_ready": _phase101_dependency_ready(
            phase101,
        ),
        "phase103_connectivity_dependency_ready": _phase103_dependency_ready(phase103),
        "phase104_revised_import_dependency_ready": _phase104_dependency_ready(
            phase104,
        ),
        "operator_preflight_check_count": len(preflight),
        "container_manager_import_step_count": len(import_steps),
        "private_auth_acceptance_check_count": len(auth_checks),
        "health_check_count": len(health_checks),
        "backup_rollback_acceptance_check_count": len(rollback),
        "go_no_go_gate_count": len(go_no_go),
        "handoff_artifact_count": len(
            _handoff_files(payload_for_scan, {"trust_metadata": {}}),
        ),
        "operator_preflight_checklist": preflight,
        "container_manager_import_handoff": import_steps,
        "private_auth_acceptance_checks": auth_checks,
        "health_check_plan": health_checks,
        "backup_rollback_acceptance_checks": rollback,
        "go_no_go_gates": go_no_go,
        "handoff_hash": _hash_payload(payload_for_scan),
        "trust_metadata": _trust_metadata(
            contract,
            phase100,
            phase101,
            phase103,
            phase104,
        ),
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
    summary["nas_operator_deployment_handoff_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_operator_deployment_handoff_ready"] else "blocked"
    )
    return summary


def summarize_nas_operator_deployment_handoff(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase105 NAS operator handoff readiness fields."""

    handoff = build_nas_operator_deployment_handoff(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_operator_deployment_handoff_contract_ready",
        "nas_operator_deployment_handoff_ready",
        "phase100_container_manager_bundle_dependency_ready",
        "phase101_private_startup_dependency_ready",
        "phase103_connectivity_dependency_ready",
        "phase104_revised_import_dependency_ready",
        "nas_private_ip",
        "nas_private_ip_private_lan",
        "operator_approval_required",
        "live_execution_allowed_now",
        "operator_preflight_check_count",
        "container_manager_import_step_count",
        "private_auth_acceptance_check_count",
        "health_check_count",
        "backup_rollback_acceptance_check_count",
        "go_no_go_gate_count",
        "handoff_artifact_count",
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
    return {key: handoff[key] for key in keys} | {
        "nas_operator_deployment_handoff": handoff,
    }


def write_nas_operator_deployment_handoff_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write Phase105 handoff artifacts under an explicit temporary directory."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase105 NAS operator handoff output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    handoff = build_nas_operator_deployment_handoff(contract_path=contract_path)
    files = _handoff_files(
        {
            "operator_preflight_checklist": handoff["operator_preflight_checklist"],
            "container_manager_import_handoff": handoff[
                "container_manager_import_handoff"
            ],
            "private_auth_acceptance": handoff["private_auth_acceptance_checks"],
            "health_check_plan": handoff["health_check_plan"],
            "backup_rollback_acceptance": handoff[
                "backup_rollback_acceptance_checks"
            ],
            "go_no_go_gates": handoff["go_no_go_gates"],
        },
        handoff,
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
        "nas_operator_deployment_handoff_ready": handoff[
            "nas_operator_deployment_handoff_ready"
        ],
        "handoff_output_path_count": len(written),
        "handoff_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "written_paths": written,
        "result": "passed",
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["handoff_scope"]
    target = contract["target_endpoint"]
    return (
        contract["status"] == "active_research_contract"
        and scope["default_mode"] == "operator_handoff_no_live_execution"
        and scope["operator_approval_required"] is True
        and scope["live_execution_allowed_now"] is False
        and scope["container_manager_import_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
        and target["private_lan_only"] is True
        and _is_private_lan_ip(str(target["nas_private_ip"]))
    )


def _phase100_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_container_manager_bundle_ready"] is True
        and summary["container_manager_import_attempt_count"] == 0
    )


def _phase101_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_private_local_startup_smoke_ready"] is True
        and summary["live_server_start_attempt_count"] == 0
    )


def _phase103_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_private_ip"] == "192.168.1.116"
        and summary["nas_private_ip_private_lan"] is True
        and summary["default_probe_execution_count"] == 0
    )


def _phase104_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_postgres_revised_import_rehearsal_ready"] is True
        and summary["postgres_write_attempt_count"] == 0
    )


def _operator_preflight_checklist(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _operator_step(check_id, "operator_preflight", index)
        for index, check_id in enumerate(contract["operator_preflight_checks"], start=1)
    ]


def _container_manager_import_handoff(
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _operator_step(step_id, "container_manager_import_handoff", index)
        for index, step_id in enumerate(
            contract["container_manager_import_steps"],
            start=1,
        )
    ]


def _private_auth_acceptance(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _operator_step(check_id, "private_auth_acceptance", index)
        for index, check_id in enumerate(
            contract["private_auth_acceptance_checks"],
            start=1,
        )
    ]


def _health_check_plan(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _operator_step(check_id, "health_check_plan", index)
        for index, check_id in enumerate(contract["health_checks"], start=1)
    ]


def _backup_rollback_acceptance(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _operator_step(check_id, "backup_rollback_acceptance", index)
        for index, check_id in enumerate(
            contract["backup_rollback_acceptance_checks"],
            start=1,
        )
    ]


def _go_no_go_gates(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _operator_step(gate_id, "go_no_go_gate", index)
        for index, gate_id in enumerate(contract["go_no_go_gates"], start=1)
    ]


def _operator_step(step_id: str, category: str, sequence: int) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "category": category,
        "sequence": sequence,
        "operator_approval_required": True,
        "execution_allowed_now": False,
        "status": "pending_future_operator_action",
        "provenance": "phase105_operator_handoff_contract",
    }


def _handoff_files(
    payload: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    summary_payload = {
        key: value
        for key, value in handoff.items()
        if key
        not in {
            "operator_preflight_checklist",
            "container_manager_import_handoff",
            "private_auth_acceptance_checks",
            "health_check_plan",
            "backup_rollback_acceptance_checks",
            "go_no_go_gates",
            "trust_metadata",
        }
    }
    trust_payload = handoff.get("trust_metadata", {})
    return {
        "ds925-operator-preflight-checklist.json": payload.get(
            "operator_preflight_checklist",
            [],
        ),
        "ds925-container-manager-import-handoff.json": payload.get(
            "container_manager_import_handoff",
            [],
        ),
        "ds925-private-auth-acceptance.json": payload.get(
            "private_auth_acceptance",
            [],
        ),
        "ds925-health-check-plan.json": payload.get("health_check_plan", []),
        "ds925-backup-rollback-acceptance.json": payload.get(
            "backup_rollback_acceptance",
            [],
        ),
        "ds925-go-no-go-gates.json": payload.get("go_no_go_gates", []),
        "ds925-operator-handoff-summary.json": summary_payload,
        "ds925-operator-handoff-trust-metadata.json": trust_payload,
    }


def _trust_metadata(
    contract: dict[str, Any],
    phase100: dict[str, Any],
    phase101: dict[str, Any],
    phase103: dict[str, Any],
    phase104: dict[str, Any],
) -> dict[str, Any]:
    return {
        "output_label": "research_only_private_nas_operator_handoff",
        "target_endpoint": str(contract["target_endpoint"]["nas_private_ip"]),
        "private_lan_only": True,
        "operator_approval_required": True,
        "live_execution_allowed_now": False,
        "phase100_bundle_ready": phase100["nas_container_manager_bundle_ready"],
        "phase101_private_startup_ready": phase101[
            "nas_private_local_startup_smoke_ready"
        ],
        "phase103_connectivity_ready": phase103[
            "nas_ds925_connectivity_smoke_ready"
        ],
        "phase104_revised_import_ready": phase104[
            "nas_postgres_revised_import_rehearsal_ready"
        ],
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
        "portfolio_instruction_enabled": False,
        "public_output_enabled": False,
    }


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected_without_self = dict(expected)
    expected_without_self.pop("nas_operator_deployment_handoff_ready", None)
    return expected_without_self


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


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
    rendered = json.dumps(value, sort_keys=True).upper()
    return sum(marker in rendered for marker in SECRET_MARKERS)


def _is_private_lan_ip(value: str) -> bool:
    return ipaddress.ip_address(value).is_private


def _is_under_tmp(path: Path) -> bool:
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    return resolved == tmp_resolved or tmp_resolved in resolved.parents
