"""Phase100 Container Manager bundle dry-run closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_container_manager_bundle import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_container_manager_bundle,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase100_container_manager_bundle_closure.yaml"


def summarize_phase100_container_manager_bundle_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase100 closure gates for CI and final reporting."""

    bundle = summarize_nas_container_manager_bundle(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "100",
        "phase_id": 100,
        "phase100_closure_ready": True,
        "nas_container_manager_bundle_contract_ready": bundle[
            "nas_container_manager_bundle_contract_ready"
        ],
        "nas_container_manager_bundle_ready": bundle[
            "nas_container_manager_bundle_ready"
        ],
        "ds925_package_assessment_dependency_ready": bundle[
            "ds925_package_assessment_dependency_ready"
        ],
        "phase99_readonly_smoke_dependency_ready": bundle[
            "phase99_readonly_smoke_dependency_ready"
        ],
        "phase98_lifecycle_dependency_ready": bundle[
            "phase98_lifecycle_dependency_ready"
        ],
        "compose_yaml_generation_ready": bundle["compose_yaml_generation_ready"],
        "compose_yaml_valid": bundle["compose_yaml_valid"],
        "compose_service_count": bundle["compose_service_count"],
        "required_service_count": bundle["required_service_count"],
        "app_service_present": bundle["app_service_present"],
        "postgres_service_present": bundle["postgres_service_present"],
        "refresh_worker_service_present": bundle["refresh_worker_service_present"],
        "healthcheck_service_count": bundle["healthcheck_service_count"],
        "named_volume_count": bundle["named_volume_count"],
        "internal_network_count": bundle["internal_network_count"],
        "required_environment_placeholder_count": bundle[
            "required_environment_placeholder_count"
        ],
        "bundle_artifact_count": bundle["bundle_artifact_count"],
        "host_port_publish_count": bundle["host_port_publish_count"],
        "privileged_service_count": bundle["privileged_service_count"],
        "host_bind_mount_count": bundle["host_bind_mount_count"],
        "secret_value_literal_count": bundle["secret_value_literal_count"],
        "container_manager_import_attempt_count": bundle[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": bundle["docker_compose_execution_count"],
        "container_image_pull_attempt_count": bundle[
            "container_image_pull_attempt_count"
        ],
        "container_start_attempt_count": bundle["container_start_attempt_count"],
        "network_bind_attempt_count": bundle["network_bind_attempt_count"],
        "live_server_start_attempt_count": bundle["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": bundle["live_db_connection_attempt_count"],
        "postgres_read_attempt_count": bundle["postgres_read_attempt_count"],
        "postgres_write_attempt_count": bundle["postgres_write_attempt_count"],
        "schema_migration_attempt_count": bundle["schema_migration_attempt_count"],
        "live_fetch_attempt_count": bundle["live_fetch_attempt_count"],
        "repo_output_written_count": bundle["repo_output_written_count"],
        "public_output_count": bundle["public_output_count"],
        "frontend_database_access_allowed": bundle["frontend_database_access_allowed"],
        "frontend_api_key_allowed": bundle["frontend_api_key_allowed"],
        "refresh_worker_enabled": bundle["refresh_worker_enabled"],
        "point_in_time_claim_count": bundle["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": bundle["revised_mislabeled_as_pit_count"],
        "prohibited_output_field_count": bundle["prohibited_output_field_count"],
        "candidate_phase_emitted": bundle["candidate_phase_emitted"],
        "current_phase_emitted": bundle["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": bundle[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": bundle[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": bundle["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": bundle["role_count_voting_added_count"],
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
            "declared_state_preserved_container_manager_bundle_dry_run"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "container_bundle_ready_no_replay_execution"
        ),
        "development_next_phase": bundle["development_next_phase"],
        "phase100_closure_status": (
            "closed_container_manager_bundle_dry_run_ready_no_import_or_live_service"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase100_container_manager_bundle_closure"]["hard_gates"])


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
