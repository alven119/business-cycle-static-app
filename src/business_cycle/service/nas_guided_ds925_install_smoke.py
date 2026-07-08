"""Guided DS925+ install and NAS-side read-only smoke plan for Phase 102.

The module prepares an operator handoff for a future DS925+ install. It does
not log into the NAS, install packages, import Container Manager bundles, pull
images, start containers, connect to Postgres, run migrations, or fetch live
macro data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml

from business_cycle.audits.nas_ds925_deployment_package_assessment import (
    summarize_nas_ds925_deployment_package_assessment,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_guided_ds925_install_smoke_contract.yaml"
)
PHASE99_CLOSURE_PATH = (
    ROOT / "specs/audits/phase99_nas_postgres_readonly_smoke_closure.yaml"
)
PHASE100_CLOSURE_PATH = (
    ROOT / "specs/audits/phase100_container_manager_bundle_closure.yaml"
)
PHASE101_CLOSURE_PATH = (
    ROOT / "specs/audits/phase101_private_local_startup_smoke_closure.yaml"
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


def load_nas_guided_ds925_install_smoke_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase102 DS925+ guided install contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_guided_ds925_install_smoke_contract"])


def build_nas_guided_ds925_install_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase102 guided install and read-only smoke plan."""

    contract = load_nas_guided_ds925_install_smoke_contract(contract_path)
    package_assessment = summarize_nas_ds925_deployment_package_assessment()
    phase101 = _load_closure_hard_gates(
        PHASE101_CLOSURE_PATH,
        "phase101_private_local_startup_smoke_closure",
    )
    phase100 = _load_closure_hard_gates(
        PHASE100_CLOSURE_PATH,
        "phase100_container_manager_bundle_closure",
    )
    phase99 = _load_closure_hard_gates(
        PHASE99_CLOSURE_PATH,
        "phase99_nas_postgres_readonly_smoke_closure",
    )
    install_runbook = _install_runbook(contract, package_assessment)
    readonly_smoke_plan = _readonly_smoke_plan(contract)
    rollback = _rollback_steps(contract)
    summary: dict[str, Any] = {
        "phase": "102",
        "phase_id": 102,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase102_nas_guided_ds925_install_smoke_plan",
        "artifact_version": contract["version"],
        "output_mode": "research_only_guided_ds925_install_plan",
        "research_only": True,
        "target_device": contract["install_scope"]["target_device"],
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_guided_ds925_install_smoke_contract_ready": _contract_ready(contract),
        "package_assessment_dependency_ready": _package_dependency_ready(
            package_assessment,
        ),
        "phase101_startup_smoke_dependency_ready": _phase101_dependency_ready(phase101),
        "phase100_bundle_dependency_ready": _phase100_dependency_ready(phase100),
        "phase99_readonly_smoke_dependency_ready": _phase99_dependency_ready(phase99),
        "guided_install_runbook_ready": _install_runbook_ready(install_runbook),
        "nas_side_readonly_smoke_plan_ready": _readonly_smoke_plan_ready(
            readonly_smoke_plan,
        ),
        "package_checklist_count": len(contract["guided_install"]["package_checklist"]),
        "recommended_package_count": int(
            package_assessment["recommended_package_count"],
        ),
        "operator_input_required_count": len(
            contract["guided_install"]["operator_inputs_required"],
        ),
        "install_step_count": len(contract["guided_install"]["install_steps"]),
        "readonly_smoke_command_preview_count": len(
            contract["guided_install"]["readonly_smoke_command_preview"],
        ),
        "readonly_smoke_command_executed_count": 0,
        "rollback_step_count": len(rollback),
        "public_internet_exposure_default": False,
        "tailscale_private_access_plan_ready": _has_step(
            install_runbook,
            "install_or_verify_tailscale",
        ),
        "container_manager_import_plan_ready": _has_step(
            install_runbook,
            "review_compose_bundle_without_importing",
        ),
        "postgres_volume_plan_ready": _has_step(install_runbook, "create_named_volumes"),
        "app_container_plan_ready": _has_step(
            install_runbook,
            "enter_secrets_in_container_manager_ui",
        ),
        "backup_plan_ready": "postgres_volume_backup_location"
        in contract["guided_install"]["operator_inputs_required"],
        "install_runbook": install_runbook,
        "readonly_smoke_plan": readonly_smoke_plan,
        "rollback_steps": rollback,
        "trust_metadata": _trust_metadata(contract),
        "actual_nas_connection_attempt_count": 0,
        "package_install_attempt_count": 0,
        "tailscale_login_attempt_count": 0,
        "container_manager_import_attempt_count": 0,
        "docker_compose_execution_count": 0,
        "container_image_pull_attempt_count": 0,
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
        "secret_value_literal_count": _secret_value_literal_count(
            {
                "install_runbook": install_runbook,
                "readonly_smoke_plan": readonly_smoke_plan,
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
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        {
            "install_runbook": install_runbook,
            "readonly_smoke_plan": readonly_smoke_plan,
            "rollback_steps": rollback,
            "trust_metadata": summary["trust_metadata"],
        },
    )
    summary["nas_guided_ds925_install_smoke_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_guided_ds925_install_smoke_ready"] else "blocked"
    )
    return summary


def summarize_nas_guided_ds925_install_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase102 DS925+ guided install fields."""

    smoke = build_nas_guided_ds925_install_smoke(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_guided_ds925_install_smoke_contract_ready",
        "nas_guided_ds925_install_smoke_ready",
        "package_assessment_dependency_ready",
        "phase101_startup_smoke_dependency_ready",
        "phase100_bundle_dependency_ready",
        "phase99_readonly_smoke_dependency_ready",
        "guided_install_runbook_ready",
        "nas_side_readonly_smoke_plan_ready",
        "package_checklist_count",
        "recommended_package_count",
        "operator_input_required_count",
        "install_step_count",
        "readonly_smoke_command_preview_count",
        "readonly_smoke_command_executed_count",
        "rollback_step_count",
        "public_internet_exposure_default",
        "tailscale_private_access_plan_ready",
        "container_manager_import_plan_ready",
        "postgres_volume_plan_ready",
        "app_container_plan_ready",
        "backup_plan_ready",
        "actual_nas_connection_attempt_count",
        "package_install_attempt_count",
        "tailscale_login_attempt_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_image_pull_attempt_count",
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
        "nas_guided_ds925_install_smoke": smoke,
    }


def write_nas_guided_ds925_install_smoke_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write guided install artifacts under an explicit temporary path."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase102 guided install output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    smoke = build_nas_guided_ds925_install_smoke(contract_path=contract_path)
    files = {
        "ds925-guided-install-runbook.json": smoke["install_runbook"],
        "nas-readonly-smoke-plan.json": smoke["readonly_smoke_plan"],
        "ds925-rollback-checklist.json": {"phase": 102, "rollback_steps": smoke["rollback_steps"]},
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
        "nas_guided_ds925_install_smoke_ready": smoke[
            "nas_guided_ds925_install_smoke_ready"
        ],
        "guided_install_output_path_count": len(written),
        "guided_install_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "written_paths": written,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "result": "passed" if smoke["result"] == "passed" else "blocked",
    }


def _install_runbook(
    contract: dict[str, Any],
    package_assessment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "phase": 102,
        "target_device": contract["install_scope"]["target_device"],
        "package_checklist": contract["guided_install"]["package_checklist"],
        "recommended_package_count": package_assessment["recommended_package_count"],
        "operator_inputs_required": contract["guided_install"][
            "operator_inputs_required"
        ],
        "install_steps": contract["guided_install"]["install_steps"],
        "execution_allowed_now": False,
        "public_internet_exposure_default": False,
        "notes_zh": (
            "此 runbook 是手把手 DS925+ 安裝前置包；本 Phase 不登入 NAS、"
            "不安裝套件、不匯入 bundle、不啟容器。"
        ),
    }


def _readonly_smoke_plan(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": 102,
        "command_preview": contract["guided_install"]["readonly_smoke_command_preview"],
        "command_execution_allowed_now": False,
        "requires_operator_on_nas": True,
        "expected_mode": "fixture_or_readonly_smoke_only",
        "must_not_write_postgres": True,
        "must_not_run_schema_migration": True,
        "must_not_fetch_live_macro_data": True,
    }


def _rollback_steps(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": step,
            "ready": True,
            "live_resource_created_by_phase": False,
        }
        for step in contract["guided_install"]["rollback_steps"]
    ]


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["install_scope"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_device"] == "Synology DS925+"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["guided_install_runbook_allowed"] is True
        and scope["nas_side_readonly_smoke_plan_allowed"] is True
        and scope["operator_assisted_execution_required"] is True
        and scope["actual_nas_connection_allowed_now"] is False
        and scope["package_install_allowed_now"] is False
        and scope["container_manager_import_allowed_now"] is False
        and scope["docker_compose_execution_allowed_now"] is False
        and scope["container_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
    )


def _package_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["result"] == "passed"
        and summary["nas_ds925_package_assessment_ready"] is True
        and summary["recommended_guided_ds925_deploy_phase"] == 102
    )


def _phase101_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["nas_private_local_startup_smoke_ready"] is True
        and summary["uvicorn_run_attempt_count"] == 0
    )


def _phase100_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["nas_container_manager_bundle_ready"] is True
        and summary["compose_service_count"] == 3
    )


def _phase99_dependency_ready(summary: dict[str, Any]) -> bool:
    return (
        summary["nas_postgres_readonly_smoke_ready"] is True
        and summary["postgres_write_attempt_count"] == 0
    )


def _load_closure_hard_gates(path: Path, root_key: str) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(payload[root_key]["hard_gates"])


def _install_runbook_ready(runbook: dict[str, Any]) -> bool:
    return (
        runbook["execution_allowed_now"] is False
        and len(runbook["package_checklist"]) == 4
        and len(runbook["install_steps"]) == 8
        and runbook["public_internet_exposure_default"] is False
    )


def _readonly_smoke_plan_ready(plan: dict[str, Any]) -> bool:
    return (
        plan["command_execution_allowed_now"] is False
        and len(plan["command_preview"]) == 2
        and plan["must_not_write_postgres"] is True
        and plan["must_not_run_schema_migration"] is True
    )


def _has_step(runbook: dict[str, Any], step_id: str) -> bool:
    return step_id in runbook["install_steps"]


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


def _trust_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "nas_migration_surface": "guided_ds925_install_and_readonly_smoke_plan",
        "target_device": contract["install_scope"]["target_device"],
        "operator_assisted_execution_required": True,
        "actual_nas_connection_attempted": False,
        "package_install_attempted": False,
        "container_manager_import_attempted": False,
        "container_started": False,
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
    expected.pop("nas_guided_ds925_install_smoke_ready", None)
    return expected
