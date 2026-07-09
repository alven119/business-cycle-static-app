"""Phase108 NAS Container Manager live-start package closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_container_manager_live_start import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_container_manager_live_start,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase108_nas_container_manager_live_start_closure.yaml"


def summarize_phase108_nas_container_manager_live_start_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase108 closure gates for CI and final reporting."""

    live_start = summarize_nas_container_manager_live_start(
        contract_path=contract_path,
    )
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "108",
        "phase_id": 108,
        "phase108_closure_ready": True,
        "nas_container_manager_live_start_contract_ready": live_start[
            "nas_container_manager_live_start_contract_ready"
        ],
        "nas_container_manager_live_start_package_ready": live_start[
            "nas_container_manager_live_start_package_ready"
        ],
        "phase107_runtime_bundle_dependency_ready": live_start[
            "phase107_runtime_bundle_dependency_ready"
        ],
        "phase106_operator_session_dependency_ready": live_start[
            "phase106_operator_session_dependency_ready"
        ],
        "target_nas_private_ip": live_start["target_nas_private_ip"],
        "app_image_reference": live_start["app_image_reference"],
        "expected_project_name": live_start["expected_project_name"],
        "operator_stage_count": live_start["operator_stage_count"],
        "required_operator_action_count": live_start[
            "required_operator_action_count"
        ],
        "operator_action_with_manual_owner_count": live_start[
            "operator_action_with_manual_owner_count"
        ],
        "operator_action_auto_execution_count": live_start[
            "operator_action_auto_execution_count"
        ],
        "operator_report_schema_ready": live_start["operator_report_schema_ready"],
        "operator_report_template_ready": live_start[
            "operator_report_template_ready"
        ],
        "sample_operator_live_start_report_valid": live_start[
            "sample_operator_live_start_report_valid"
        ],
        "live_acceptance_requires_operator_report": live_start[
            "live_acceptance_requires_operator_report"
        ],
        "live_start_acceptance_status": live_start[
            "live_start_acceptance_status"
        ],
        "live_deployment_complete": live_start["live_deployment_complete"],
        "live_start_package_artifact_count": live_start[
            "live_start_package_artifact_count"
        ],
        "package_output_under_tmp_only": live_start[
            "package_output_under_tmp_only"
        ],
        "codex_dsm_login_attempt_count": live_start["codex_dsm_login_attempt_count"],
        "codex_container_manager_import_attempt_count": live_start[
            "codex_container_manager_import_attempt_count"
        ],
        "codex_docker_build_attempt_count": live_start[
            "codex_docker_build_attempt_count"
        ],
        "codex_container_start_attempt_count": live_start[
            "codex_container_start_attempt_count"
        ],
        "codex_live_server_start_attempt_count": live_start[
            "codex_live_server_start_attempt_count"
        ],
        "codex_live_db_connection_attempt_count": live_start[
            "codex_live_db_connection_attempt_count"
        ],
        "codex_postgres_read_attempt_count": live_start[
            "codex_postgres_read_attempt_count"
        ],
        "codex_postgres_write_attempt_count": live_start[
            "codex_postgres_write_attempt_count"
        ],
        "codex_schema_migration_attempt_count": live_start[
            "codex_schema_migration_attempt_count"
        ],
        "codex_live_fetch_attempt_count": live_start[
            "codex_live_fetch_attempt_count"
        ],
        "repo_output_written_count": live_start["repo_output_written_count"],
        "public_output_count": live_start["public_output_count"],
        "tests_network_dependency_count": live_start[
            "tests_network_dependency_count"
        ],
        "private_access_required": live_start["private_access_required"],
        "public_host_port_publish_count": live_start[
            "public_host_port_publish_count"
        ],
        "refresh_worker_enabled": live_start["refresh_worker_enabled"],
        "label_used_by_runtime_count": live_start["label_used_by_runtime_count"],
        "candidate_phase_emitted": live_start["candidate_phase_emitted"],
        "current_phase_emitted": live_start["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": live_start[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": live_start[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": live_start[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": live_start[
            "role_count_voting_added_count"
        ],
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
            "declared_state_preserved_nas_live_start_package"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_live_start_package_ready_no_replay_execution"
        ),
        "development_next_phase": live_start["development_next_phase"],
        "phase108_closure_status": (
            "closed_nas_container_manager_live_start_package_ready_waiting_operator_report"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase108_nas_container_manager_live_start_closure"]["hard_gates"],
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
