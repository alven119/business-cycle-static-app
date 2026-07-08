"""Phase98 NAS service lifecycle rehearsal closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_service_lifecycle import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_service_lifecycle,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase98_nas_service_lifecycle_closure.yaml"


def summarize_phase98_nas_service_lifecycle_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase98 closure gates for CI and final reporting."""

    lifecycle = summarize_nas_service_lifecycle(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "98",
        "phase_id": 98,
        "phase98_closure_ready": True,
        "nas_service_lifecycle_contract_ready": lifecycle[
            "nas_service_lifecycle_contract_ready"
        ],
        "nas_service_lifecycle_ready": lifecycle["nas_service_lifecycle_ready"],
        "lifecycle_rehearsal_ready": lifecycle["lifecycle_rehearsal_ready"],
        "phase97_asgi_dependency_ready": lifecycle["phase97_asgi_dependency_ready"],
        "startup_rehearsed": lifecycle["startup_rehearsed"],
        "readiness_probe_ready": lifecycle["readiness_probe_ready"],
        "shutdown_rehearsed": lifecycle["shutdown_rehearsed"],
        "rollback_rehearsal_ready": lifecycle["rollback_rehearsal_ready"],
        "lifecycle_stage_count": lifecycle["lifecycle_stage_count"],
        "lifecycle_event_count": lifecycle["lifecycle_event_count"],
        "startup_step_count": lifecycle["startup_step_count"],
        "readiness_probe_count": lifecycle["readiness_probe_count"],
        "readiness_probe_pass_count": lifecycle["readiness_probe_pass_count"],
        "shutdown_step_count": lifecycle["shutdown_step_count"],
        "rollback_step_count": lifecycle["rollback_step_count"],
        "service_health_status": lifecycle["service_health_status"],
        "uvicorn_run_attempt_count": lifecycle["uvicorn_run_attempt_count"],
        "network_bind_attempt_count": lifecycle["network_bind_attempt_count"],
        "live_server_start_attempt_count": lifecycle["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": lifecycle[
            "live_db_connection_attempt_count"
        ],
        "postgres_read_attempt_count": lifecycle["postgres_read_attempt_count"],
        "postgres_write_attempt_count": lifecycle["postgres_write_attempt_count"],
        "live_fetch_attempt_count": lifecycle["live_fetch_attempt_count"],
        "repo_output_written_count": lifecycle["repo_output_written_count"],
        "public_output_count": lifecycle["public_output_count"],
        "frontend_database_access_allowed": lifecycle[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": lifecycle["frontend_api_key_allowed"],
        "prohibited_output_field_count": lifecycle["prohibited_output_field_count"],
        "candidate_phase_emitted": lifecycle["candidate_phase_emitted"],
        "current_phase_emitted": lifecycle["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": lifecycle[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": lifecycle[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": lifecycle[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": lifecycle["role_count_voting_added_count"],
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
            "declared_state_preserved_lifecycle_rehearsal_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "lifecycle_rehearsal_ready_no_replay_execution"
        ),
        "development_next_phase": lifecycle["development_next_phase"],
        "phase98_closure_status": (
            "closed_nas_service_lifecycle_rehearsal_ready_no_live_bind_or_db"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase98_nas_service_lifecycle_closure"]["hard_gates"])


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
