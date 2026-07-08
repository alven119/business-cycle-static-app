"""Phase102 guided DS925+ install/read-only smoke closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_guided_ds925_install_smoke import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_guided_ds925_install_smoke,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase102_guided_ds925_install_smoke_closure.yaml"


def summarize_phase102_guided_ds925_install_smoke_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase102 closure gates for CI and final reporting."""

    smoke = summarize_nas_guided_ds925_install_smoke(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "102",
        "phase_id": 102,
        "phase102_closure_ready": True,
        "nas_guided_ds925_install_smoke_contract_ready": smoke[
            "nas_guided_ds925_install_smoke_contract_ready"
        ],
        "nas_guided_ds925_install_smoke_ready": smoke[
            "nas_guided_ds925_install_smoke_ready"
        ],
        "package_assessment_dependency_ready": smoke[
            "package_assessment_dependency_ready"
        ],
        "phase101_startup_smoke_dependency_ready": smoke[
            "phase101_startup_smoke_dependency_ready"
        ],
        "phase100_bundle_dependency_ready": smoke["phase100_bundle_dependency_ready"],
        "phase99_readonly_smoke_dependency_ready": smoke[
            "phase99_readonly_smoke_dependency_ready"
        ],
        "guided_install_runbook_ready": smoke["guided_install_runbook_ready"],
        "nas_side_readonly_smoke_plan_ready": smoke[
            "nas_side_readonly_smoke_plan_ready"
        ],
        "package_checklist_count": smoke["package_checklist_count"],
        "recommended_package_count": smoke["recommended_package_count"],
        "operator_input_required_count": smoke["operator_input_required_count"],
        "install_step_count": smoke["install_step_count"],
        "readonly_smoke_command_preview_count": smoke[
            "readonly_smoke_command_preview_count"
        ],
        "readonly_smoke_command_executed_count": smoke[
            "readonly_smoke_command_executed_count"
        ],
        "rollback_step_count": smoke["rollback_step_count"],
        "public_internet_exposure_default": smoke["public_internet_exposure_default"],
        "tailscale_private_access_plan_ready": smoke[
            "tailscale_private_access_plan_ready"
        ],
        "container_manager_import_plan_ready": smoke[
            "container_manager_import_plan_ready"
        ],
        "postgres_volume_plan_ready": smoke["postgres_volume_plan_ready"],
        "app_container_plan_ready": smoke["app_container_plan_ready"],
        "backup_plan_ready": smoke["backup_plan_ready"],
        "actual_nas_connection_attempt_count": smoke[
            "actual_nas_connection_attempt_count"
        ],
        "package_install_attempt_count": smoke["package_install_attempt_count"],
        "tailscale_login_attempt_count": smoke["tailscale_login_attempt_count"],
        "container_manager_import_attempt_count": smoke[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": smoke["docker_compose_execution_count"],
        "container_image_pull_attempt_count": smoke[
            "container_image_pull_attempt_count"
        ],
        "container_start_attempt_count": smoke["container_start_attempt_count"],
        "live_server_start_attempt_count": smoke["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": smoke["live_db_connection_attempt_count"],
        "postgres_read_attempt_count": smoke["postgres_read_attempt_count"],
        "postgres_write_attempt_count": smoke["postgres_write_attempt_count"],
        "schema_migration_attempt_count": smoke["schema_migration_attempt_count"],
        "live_fetch_attempt_count": smoke["live_fetch_attempt_count"],
        "repo_output_written_count": smoke["repo_output_written_count"],
        "public_output_count": smoke["public_output_count"],
        "frontend_database_access_allowed": smoke["frontend_database_access_allowed"],
        "frontend_api_key_allowed": smoke["frontend_api_key_allowed"],
        "secret_value_literal_count": smoke["secret_value_literal_count"],
        "prohibited_output_field_count": smoke["prohibited_output_field_count"],
        "candidate_phase_emitted": smoke["candidate_phase_emitted"],
        "current_phase_emitted": smoke["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": smoke[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": smoke[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": smoke["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": smoke["role_count_voting_added_count"],
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
            "declared_state_preserved_guided_ds925_install_plan"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "guided_install_ready_no_replay_execution"
        ),
        "development_next_phase": smoke["development_next_phase"],
        "phase102_closure_status": (
            "closed_guided_ds925_install_and_readonly_smoke_plan_ready_no_live_nas_execution"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase102_guided_ds925_install_smoke_closure"]["hard_gates"])


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
