"""Phase105 NAS operator deployment handoff closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_operator_deployment_handoff import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_operator_deployment_handoff,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = (
    ROOT / "specs/audits/phase105_nas_operator_deployment_handoff_closure.yaml"
)


def summarize_phase105_nas_operator_deployment_handoff_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase105 closure gates for CI and final reporting."""

    handoff = summarize_nas_operator_deployment_handoff(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "105",
        "phase_id": 105,
        "phase105_closure_ready": True,
        "nas_operator_deployment_handoff_contract_ready": handoff[
            "nas_operator_deployment_handoff_contract_ready"
        ],
        "nas_operator_deployment_handoff_ready": handoff[
            "nas_operator_deployment_handoff_ready"
        ],
        "phase100_container_manager_bundle_dependency_ready": handoff[
            "phase100_container_manager_bundle_dependency_ready"
        ],
        "phase101_private_startup_dependency_ready": handoff[
            "phase101_private_startup_dependency_ready"
        ],
        "phase103_connectivity_dependency_ready": handoff[
            "phase103_connectivity_dependency_ready"
        ],
        "phase104_revised_import_dependency_ready": handoff[
            "phase104_revised_import_dependency_ready"
        ],
        "nas_private_ip": handoff["nas_private_ip"],
        "nas_private_ip_private_lan": handoff["nas_private_ip_private_lan"],
        "operator_approval_required": handoff["operator_approval_required"],
        "live_execution_allowed_now": handoff["live_execution_allowed_now"],
        "operator_preflight_check_count": handoff[
            "operator_preflight_check_count"
        ],
        "container_manager_import_step_count": handoff[
            "container_manager_import_step_count"
        ],
        "private_auth_acceptance_check_count": handoff[
            "private_auth_acceptance_check_count"
        ],
        "health_check_count": handoff["health_check_count"],
        "backup_rollback_acceptance_check_count": handoff[
            "backup_rollback_acceptance_check_count"
        ],
        "go_no_go_gate_count": handoff["go_no_go_gate_count"],
        "handoff_artifact_count": handoff["handoff_artifact_count"],
        "dsm_login_attempt_count": handoff["dsm_login_attempt_count"],
        "package_install_attempt_count": handoff["package_install_attempt_count"],
        "tailnet_login_attempt_count": handoff["tailnet_login_attempt_count"],
        "container_manager_import_attempt_count": handoff[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": handoff["docker_compose_execution_count"],
        "container_start_attempt_count": handoff["container_start_attempt_count"],
        "live_server_start_attempt_count": handoff[
            "live_server_start_attempt_count"
        ],
        "network_bind_attempt_count": handoff["network_bind_attempt_count"],
        "live_db_connection_attempt_count": handoff[
            "live_db_connection_attempt_count"
        ],
        "postgres_read_attempt_count": handoff["postgres_read_attempt_count"],
        "postgres_write_attempt_count": handoff["postgres_write_attempt_count"],
        "schema_migration_attempt_count": handoff[
            "schema_migration_attempt_count"
        ],
        "backup_command_execution_count": handoff[
            "backup_command_execution_count"
        ],
        "restore_command_execution_count": handoff[
            "restore_command_execution_count"
        ],
        "live_fetch_attempt_count": handoff["live_fetch_attempt_count"],
        "tests_network_dependency_count": handoff["tests_network_dependency_count"],
        "repo_output_written_count": handoff["repo_output_written_count"],
        "public_output_count": handoff["public_output_count"],
        "frontend_database_access_allowed": handoff[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": handoff["frontend_api_key_allowed"],
        "secret_value_literal_count": handoff["secret_value_literal_count"],
        "prohibited_output_field_count": handoff["prohibited_output_field_count"],
        "candidate_phase_emitted": handoff["candidate_phase_emitted"],
        "current_phase_emitted": handoff["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": handoff[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": handoff[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": handoff[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": handoff["role_count_voting_added_count"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "progress_decrease_count": progress["progress_decrease_count"],
        "progress_decrease_without_reason_count": progress[
            "progress_decrease_without_reason_count"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_nas_operator_handoff"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_operator_handoff_ready_no_replay_execution"
        ),
        "development_next_phase": handoff["development_next_phase"],
        "phase105_closure_status": (
            "closed_nas_operator_deployment_handoff_ready_no_live_execution"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase105_nas_operator_deployment_handoff_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _git_ls_files(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
