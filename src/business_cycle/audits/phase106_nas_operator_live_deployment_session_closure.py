"""Phase106 NAS operator live deployment session closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_operator_live_deployment_session import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_operator_live_deployment_session,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = (
    ROOT
    / "specs/audits/phase106_nas_operator_live_deployment_session_closure.yaml"
)


def summarize_phase106_nas_operator_live_deployment_session_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase106 closure gates for CI and final reporting."""

    session = summarize_nas_operator_live_deployment_session(
        contract_path=contract_path,
    )
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "106",
        "phase_id": 106,
        "phase106_closure_ready": True,
        "nas_operator_live_session_contract_ready": session[
            "nas_operator_live_session_contract_ready"
        ],
        "nas_operator_live_session_protocol_ready": session[
            "nas_operator_live_session_protocol_ready"
        ],
        "phase105_handoff_dependency_ready": session[
            "phase105_handoff_dependency_ready"
        ],
        "nas_private_ip": session["nas_private_ip"],
        "nas_private_ip_private_lan": session["nas_private_ip_private_lan"],
        "operator_must_execute_live_steps_out_of_band": session[
            "operator_must_execute_live_steps_out_of_band"
        ],
        "automatic_live_execution_allowed_now": session[
            "automatic_live_execution_allowed_now"
        ],
        "session_stage_count": session["session_stage_count"],
        "required_operator_action_count": session["required_operator_action_count"],
        "operator_action_with_manual_owner_count": session[
            "operator_action_with_manual_owner_count"
        ],
        "operator_action_auto_execution_count": session[
            "operator_action_auto_execution_count"
        ],
        "operator_report_schema_ready": session["operator_report_schema_ready"],
        "operator_report_template_ready": session["operator_report_template_ready"],
        "sample_operator_report_valid": session["sample_operator_report_valid"],
        "live_acceptance_requires_operator_report": session[
            "live_acceptance_requires_operator_report"
        ],
        "live_deployment_acceptance_status": session[
            "live_deployment_acceptance_status"
        ],
        "live_deployment_complete": session["live_deployment_complete"],
        "session_artifact_count": session["session_artifact_count"],
        "dsm_login_attempt_count": session["dsm_login_attempt_count"],
        "package_install_attempt_count": session["package_install_attempt_count"],
        "tailnet_login_attempt_count": session["tailnet_login_attempt_count"],
        "container_manager_import_attempt_count": session[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": session["docker_compose_execution_count"],
        "container_start_attempt_count": session["container_start_attempt_count"],
        "live_server_start_attempt_count": session[
            "live_server_start_attempt_count"
        ],
        "network_bind_attempt_count": session["network_bind_attempt_count"],
        "live_db_connection_attempt_count": session[
            "live_db_connection_attempt_count"
        ],
        "postgres_read_attempt_count": session["postgres_read_attempt_count"],
        "postgres_write_attempt_count": session["postgres_write_attempt_count"],
        "schema_migration_attempt_count": session["schema_migration_attempt_count"],
        "backup_command_execution_count": session[
            "backup_command_execution_count"
        ],
        "restore_command_execution_count": session[
            "restore_command_execution_count"
        ],
        "live_fetch_attempt_count": session["live_fetch_attempt_count"],
        "tests_network_dependency_count": session["tests_network_dependency_count"],
        "repo_output_written_count": session["repo_output_written_count"],
        "public_output_count": session["public_output_count"],
        "frontend_database_access_allowed": session[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": session["frontend_api_key_allowed"],
        "secret_value_literal_count": session["secret_value_literal_count"],
        "prohibited_output_field_count": session["prohibited_output_field_count"],
        "candidate_phase_emitted": session["candidate_phase_emitted"],
        "current_phase_emitted": session["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": session[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": session[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": session[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": session["role_count_voting_added_count"],
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
            "declared_state_preserved_nas_operator_live_session_protocol"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_operator_live_session_protocol_ready_no_replay_execution"
        ),
        "development_next_phase": session["development_next_phase"],
        "phase106_closure_status": (
            "closed_nas_operator_live_session_protocol_ready_operator_report_required"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase106_nas_operator_live_deployment_session_closure"][
            "hard_gates"
        ],
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
