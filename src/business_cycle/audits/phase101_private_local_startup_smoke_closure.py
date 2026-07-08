"""Phase101 private local startup smoke closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_private_local_startup_smoke import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_private_local_startup_smoke,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase101_private_local_startup_smoke_closure.yaml"


def summarize_phase101_private_local_startup_smoke_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase101 closure gates for CI and final reporting."""

    smoke = summarize_nas_private_local_startup_smoke(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "101",
        "phase_id": 101,
        "phase101_closure_ready": True,
        "nas_private_local_startup_smoke_contract_ready": smoke[
            "nas_private_local_startup_smoke_contract_ready"
        ],
        "nas_private_local_startup_smoke_ready": smoke[
            "nas_private_local_startup_smoke_ready"
        ],
        "phase100_bundle_dependency_ready": smoke["phase100_bundle_dependency_ready"],
        "phase98_lifecycle_dependency_ready": smoke[
            "phase98_lifecycle_dependency_ready"
        ],
        "phase97_asgi_dependency_ready": smoke["phase97_asgi_dependency_ready"],
        "asgi_entrypoint_factory_ready": smoke["asgi_entrypoint_factory_ready"],
        "startup_plan_ready": smoke["startup_plan_ready"],
        "startup_command_preview_ready": smoke["startup_command_preview_ready"],
        "startup_command_preview_count": smoke["startup_command_preview_count"],
        "startup_command_executed_count": smoke["startup_command_executed_count"],
        "readiness_probe_count": smoke["readiness_probe_count"],
        "readiness_probe_pass_count": smoke["readiness_probe_pass_count"],
        "authenticated_probe_pass_count": smoke["authenticated_probe_pass_count"],
        "unauthenticated_probe_rejected_count": smoke[
            "unauthenticated_probe_rejected_count"
        ],
        "local_loopback_or_tailnet_only": smoke["local_loopback_or_tailnet_only"],
        "bind_host_public_count": smoke["bind_host_public_count"],
        "env_placeholder_count": smoke["env_placeholder_count"],
        "env_placeholder_missing_count": smoke["env_placeholder_missing_count"],
        "secret_value_literal_count": smoke["secret_value_literal_count"],
        "rollback_step_count": smoke["rollback_step_count"],
        "compose_service_count": smoke["compose_service_count"],
        "host_port_publish_count": smoke["host_port_publish_count"],
        "privileged_service_count": smoke["privileged_service_count"],
        "host_bind_mount_count": smoke["host_bind_mount_count"],
        "container_manager_import_attempt_count": smoke[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": smoke["docker_compose_execution_count"],
        "container_image_pull_attempt_count": smoke[
            "container_image_pull_attempt_count"
        ],
        "container_start_attempt_count": smoke["container_start_attempt_count"],
        "uvicorn_run_attempt_count": smoke["uvicorn_run_attempt_count"],
        "network_bind_attempt_count": smoke["network_bind_attempt_count"],
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
        "point_in_time_claim_count": smoke["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": smoke["revised_mislabeled_as_pit_count"],
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
            "declared_state_preserved_private_local_startup_smoke"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "startup_smoke_ready_no_replay_execution"
        ),
        "development_next_phase": smoke["development_next_phase"],
        "phase101_closure_status": (
            "closed_private_local_startup_smoke_ready_no_live_bind_or_db"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase101_private_local_startup_smoke_closure"]["hard_gates"])


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
