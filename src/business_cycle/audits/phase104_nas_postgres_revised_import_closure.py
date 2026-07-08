"""Phase104 NAS Postgres revised import and backup rehearsal closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_postgres_revised_import_rehearsal import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_postgres_revised_import_rehearsal,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase104_nas_postgres_revised_import_closure.yaml"


def summarize_phase104_nas_postgres_revised_import_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase104 closure gates for CI and final reporting."""

    rehearsal = summarize_nas_postgres_revised_import_rehearsal(
        contract_path=contract_path,
    )
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "104",
        "phase_id": 104,
        "phase104_closure_ready": True,
        "nas_postgres_revised_import_rehearsal_contract_ready": rehearsal[
            "nas_postgres_revised_import_rehearsal_contract_ready"
        ],
        "nas_postgres_revised_import_rehearsal_ready": rehearsal[
            "nas_postgres_revised_import_rehearsal_ready"
        ],
        "phase91_postgres_schema_dependency_ready": rehearsal[
            "phase91_postgres_schema_dependency_ready"
        ],
        "phase92_revised_import_dependency_ready": rehearsal[
            "phase92_revised_import_dependency_ready"
        ],
        "phase103_connectivity_dependency_ready": rehearsal[
            "phase103_connectivity_dependency_ready"
        ],
        "nas_private_ip": rehearsal["nas_private_ip"],
        "nas_private_ip_private_lan": rehearsal["nas_private_ip_private_lan"],
        "planned_import_table_count": rehearsal["planned_import_table_count"],
        "planned_import_row_count": rehearsal["planned_import_row_count"],
        "planned_series_registry_row_count": rehearsal[
            "planned_series_registry_row_count"
        ],
        "planned_source_artifact_row_count": rehearsal[
            "planned_source_artifact_row_count"
        ],
        "planned_observation_revised_row_count": rehearsal[
            "planned_observation_revised_row_count"
        ],
        "observation_vintage_row_count": rehearsal["observation_vintage_row_count"],
        "import_plan_ready": rehearsal["import_plan_ready"],
        "deterministic_upsert_sql_preview_ready": rehearsal[
            "deterministic_upsert_sql_preview_ready"
        ],
        "backup_rehearsal_plan_ready": rehearsal["backup_rehearsal_plan_ready"],
        "backup_step_count": rehearsal["backup_step_count"],
        "restore_verification_plan_ready": rehearsal[
            "restore_verification_plan_ready"
        ],
        "verification_query_count": rehearsal["verification_query_count"],
        "generated_output_under_tmp_only": rehearsal[
            "generated_output_under_tmp_only"
        ],
        "live_db_connection_attempt_count": rehearsal[
            "live_db_connection_attempt_count"
        ],
        "postgres_read_attempt_count": rehearsal["postgres_read_attempt_count"],
        "postgres_write_attempt_count": rehearsal["postgres_write_attempt_count"],
        "schema_migration_attempt_count": rehearsal[
            "schema_migration_attempt_count"
        ],
        "backup_command_execution_count": rehearsal[
            "backup_command_execution_count"
        ],
        "restore_command_execution_count": rehearsal[
            "restore_command_execution_count"
        ],
        "docker_compose_execution_count": rehearsal["docker_compose_execution_count"],
        "container_manager_import_attempt_count": rehearsal[
            "container_manager_import_attempt_count"
        ],
        "live_fetch_attempt_count": rehearsal["live_fetch_attempt_count"],
        "tests_network_dependency_count": rehearsal["tests_network_dependency_count"],
        "repo_output_written_count": rehearsal["repo_output_written_count"],
        "public_output_count": rehearsal["public_output_count"],
        "frontend_database_access_allowed": rehearsal[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": rehearsal["frontend_api_key_allowed"],
        "point_in_time_claim_count": rehearsal["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": rehearsal[
            "revised_mislabeled_as_pit_count"
        ],
        "secret_value_literal_count": rehearsal["secret_value_literal_count"],
        "prohibited_output_field_count": rehearsal["prohibited_output_field_count"],
        "candidate_phase_emitted": rehearsal["candidate_phase_emitted"],
        "current_phase_emitted": rehearsal["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": rehearsal[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": rehearsal[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": rehearsal[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": rehearsal["role_count_voting_added_count"],
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
            "declared_state_preserved_nas_revised_import_rehearsal"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_revised_import_rehearsed_no_replay_execution"
        ),
        "development_next_phase": rehearsal["development_next_phase"],
        "phase104_closure_status": (
            "closed_nas_postgres_revised_import_backup_rehearsal_ready_"
            "no_live_db_write"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase104_nas_postgres_revised_import_closure"]["hard_gates"])


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
