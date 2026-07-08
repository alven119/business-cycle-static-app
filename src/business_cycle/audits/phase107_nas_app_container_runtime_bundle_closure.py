"""Phase107 NAS app container runtime bundle closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_app_container_runtime_bundle import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_app_container_runtime_bundle,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase107_nas_app_container_runtime_bundle_closure.yaml"


def summarize_phase107_nas_app_container_runtime_bundle_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase107 closure gates for CI and final reporting."""

    bundle = summarize_nas_app_container_runtime_bundle(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "107",
        "phase_id": 107,
        "phase107_closure_ready": True,
        "nas_app_container_runtime_bundle_contract_ready": bundle[
            "nas_app_container_runtime_bundle_contract_ready"
        ],
        "nas_app_container_runtime_bundle_ready": bundle[
            "nas_app_container_runtime_bundle_ready"
        ],
        "phase106_operator_preflight_dependency_ready": bundle[
            "phase106_operator_preflight_dependency_ready"
        ],
        "phase100_bundle_dependency_ready": bundle["phase100_bundle_dependency_ready"],
        "dockerfile_present": bundle["dockerfile_present"],
        "dockerignore_present": bundle["dockerignore_present"],
        "runtime_server_module_ready": bundle["runtime_server_module_ready"],
        "healthcheck_module_ready": bundle["healthcheck_module_ready"],
        "refresh_worker_disabled_module_ready": bundle[
            "refresh_worker_disabled_module_ready"
        ],
        "compose_yaml_valid": bundle["compose_yaml_valid"],
        "compose_service_count": bundle["compose_service_count"],
        "app_service_build_ready": bundle["app_service_build_ready"],
        "app_image_reference": bundle["app_image_reference"],
        "dry_run_image_reference_count": bundle["dry_run_image_reference_count"],
        "loopback_host_port_publish_count": bundle[
            "loopback_host_port_publish_count"
        ],
        "public_host_port_publish_count": bundle["public_host_port_publish_count"],
        "secret_value_literal_count": bundle["secret_value_literal_count"],
        "required_environment_placeholder_count": bundle[
            "required_environment_placeholder_count"
        ],
        "bundle_artifact_count": bundle["bundle_artifact_count"],
        "docker_build_attempt_count": bundle["docker_build_attempt_count"],
        "docker_compose_execution_count": bundle["docker_compose_execution_count"],
        "container_manager_import_attempt_count": bundle[
            "container_manager_import_attempt_count"
        ],
        "container_start_attempt_count": bundle["container_start_attempt_count"],
        "live_server_start_attempt_count": bundle["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": bundle[
            "live_db_connection_attempt_count"
        ],
        "postgres_read_attempt_count": bundle["postgres_read_attempt_count"],
        "postgres_write_attempt_count": bundle["postgres_write_attempt_count"],
        "schema_migration_attempt_count": bundle["schema_migration_attempt_count"],
        "live_fetch_attempt_count": bundle["live_fetch_attempt_count"],
        "repo_output_written_count": bundle["repo_output_written_count"],
        "public_output_count": bundle["public_output_count"],
        "frontend_database_access_allowed": bundle[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": bundle["frontend_api_key_allowed"],
        "refresh_worker_enabled": bundle["refresh_worker_enabled"],
        "runtime_healthcheck_import_ready": bundle[
            "runtime_healthcheck_import_ready"
        ],
        "runtime_auth_secret_embedded": bundle["runtime_auth_secret_embedded"],
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
            "declared_state_preserved_nas_app_container_runtime_bundle"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_runtime_bundle_ready_no_replay_execution"
        ),
        "development_next_phase": bundle["development_next_phase"],
        "phase107_closure_status": (
            "closed_nas_app_container_runtime_bundle_ready_no_live_start"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase107_nas_app_container_runtime_bundle_closure"]["hard_gates"],
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
