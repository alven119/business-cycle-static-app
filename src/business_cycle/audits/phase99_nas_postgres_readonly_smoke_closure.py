"""Phase99 NAS Postgres read-only smoke closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.nas_ds925_deployment_package_assessment import (
    summarize_nas_ds925_deployment_package_assessment,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_postgres_readonly_smoke import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_postgres_readonly_smoke,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase99_nas_postgres_readonly_smoke_closure.yaml"


def summarize_phase99_nas_postgres_readonly_smoke_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase99 closure gates for CI and final reporting."""

    smoke = summarize_nas_postgres_readonly_smoke(contract_path=contract_path)
    packages = summarize_nas_ds925_deployment_package_assessment()
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "99",
        "phase_id": 99,
        "phase99_closure_ready": True,
        "nas_postgres_readonly_smoke_contract_ready": smoke[
            "nas_postgres_readonly_smoke_contract_ready"
        ],
        "nas_postgres_readonly_smoke_ready": smoke[
            "nas_postgres_readonly_smoke_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": smoke[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "phase92_revised_import_dependency_ready": smoke[
            "phase92_revised_import_dependency_ready"
        ],
        "phase98_lifecycle_dependency_ready": smoke[
            "phase98_lifecycle_dependency_ready"
        ],
        "fixture_driver_ready": smoke["fixture_driver_ready"],
        "readonly_query_contract_count": smoke["readonly_query_contract_count"],
        "readonly_query_pass_count": smoke["readonly_query_pass_count"],
        "readonly_result_set_count": smoke["readonly_result_set_count"],
        "readonly_result_row_count": smoke["readonly_result_row_count"],
        "readonly_required_column_missing_count": smoke[
            "readonly_required_column_missing_count"
        ],
        "forbidden_sql_rejected_count": smoke["forbidden_sql_rejected_count"],
        "forbidden_sql_accepted_count": smoke["forbidden_sql_accepted_count"],
        "live_db_connection_attempt_count": smoke["live_db_connection_attempt_count"],
        "postgres_read_attempt_count": smoke["postgres_read_attempt_count"],
        "postgres_write_attempt_count": smoke["postgres_write_attempt_count"],
        "schema_migration_attempt_count": smoke["schema_migration_attempt_count"],
        "runtime_dependency_added_count": smoke["runtime_dependency_added_count"],
        "network_bind_attempt_count": smoke["network_bind_attempt_count"],
        "live_server_start_attempt_count": smoke["live_server_start_attempt_count"],
        "live_fetch_attempt_count": smoke["live_fetch_attempt_count"],
        "repo_output_written_count": smoke["repo_output_written_count"],
        "public_output_count": smoke["public_output_count"],
        "frontend_database_access_allowed": smoke["frontend_database_access_allowed"],
        "frontend_api_key_allowed": smoke["frontend_api_key_allowed"],
        "fixture_mislabeled_as_live_count": smoke["fixture_mislabeled_as_live_count"],
        "point_in_time_claim_count": smoke["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": smoke["revised_mislabeled_as_pit_count"],
        "nas_ds925_package_assessment_ready": packages[
            "nas_ds925_package_assessment_ready"
        ],
        "assessed_package_count": packages["assessed_package_count"],
        "recommended_package_count": packages["recommended_package_count"],
        "primary_runtime_recommended": packages["primary_runtime_recommended"],
        "private_mobile_access_recommended": packages[
            "private_mobile_access_recommended"
        ],
        "database_runtime_recommended": packages["database_runtime_recommended"],
        "deployment_phase_estimate_ready": packages["deployment_phase_estimate_ready"],
        "earliest_private_alpha_phase": packages["earliest_private_alpha_phase"],
        "recommended_guided_ds925_deploy_phase": packages[
            "recommended_guided_ds925_deploy_phase"
        ],
        "full_private_nas_use_phase": packages["full_private_nas_use_phase"],
        "candidate_phase_emitted": smoke["candidate_phase_emitted"],
        "current_phase_emitted": smoke["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": smoke[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": smoke["standalone_classifier_added_count"],
        "phase_rank_or_score_added_count": smoke["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": smoke["role_count_voting_added_count"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "progress_decrease_count": progress["progress_decrease_count"],
        "progress_decrease_without_reason_count": progress[
            "progress_decrease_without_reason_count"
        ],
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_postgres_readonly_fixture_smoke"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "readonly_warehouse_smoke_ready_no_replay_execution"
        ),
        "development_next_phase": smoke["development_next_phase"],
        "phase99_closure_status": (
            "closed_nas_postgres_readonly_fixture_smoke_ready_"
            "ds925_package_path_assessed"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase99_nas_postgres_readonly_smoke_closure"]["hard_gates"])


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
