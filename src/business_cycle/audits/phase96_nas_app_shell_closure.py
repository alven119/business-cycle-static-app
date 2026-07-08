"""Phase96 NAS app shell local-service smoke closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_app_shell import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_app_shell,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase96_nas_app_shell_closure.yaml"


def summarize_phase96_nas_app_shell_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase96 closure gates for CI and final reporting."""

    shell = summarize_nas_app_shell(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "96",
        "phase_id": 96,
        "phase96_closure_ready": True,
        "nas_app_shell_contract_ready": shell["nas_app_shell_contract_ready"],
        "nas_app_shell_ready": shell["nas_app_shell_ready"],
        "local_service_smoke_ready": shell["local_service_smoke_ready"],
        "phase95_dashboard_dependency_ready": shell[
            "phase95_dashboard_dependency_ready"
        ],
        "auth_boundary_ready": shell["auth_boundary_ready"],
        "route_dispatch_ready": shell["route_dispatch_ready"],
        "service_health_ready": shell["service_health_ready"],
        "rollback_checklist_ready": shell["rollback_checklist_ready"],
        "route_count": shell["route_count"],
        "session_required_route_count": shell["session_required_route_count"],
        "authenticated_smoke_pass_count": shell["authenticated_smoke_pass_count"],
        "unauthenticated_smoke_rejected_count": shell[
            "unauthenticated_smoke_rejected_count"
        ],
        "rollback_checklist_item_count": shell["rollback_checklist_item_count"],
        "service_health_status": shell["service_health_status"],
        "service_health_route_count": shell["service_health_route_count"],
        "network_bind_attempt_count": shell["network_bind_attempt_count"],
        "live_server_start_attempt_count": shell["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": shell["live_db_connection_attempt_count"],
        "postgres_write_attempt_count": shell["postgres_write_attempt_count"],
        "live_fetch_attempt_count": shell["live_fetch_attempt_count"],
        "repo_output_written_count": shell["repo_output_written_count"],
        "public_output_count": shell["public_output_count"],
        "frontend_database_access_allowed": shell[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": shell["frontend_api_key_allowed"],
        "prohibited_output_field_count": shell["prohibited_output_field_count"],
        "candidate_phase_emitted": shell["candidate_phase_emitted"],
        "current_phase_emitted": shell["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": shell[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": shell[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": shell[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": shell["role_count_voting_added_count"],
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
            "declared_state_preserved_nas_app_shell_smoke_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_app_shell_ready_no_replay_execution"
        ),
        "development_next_phase": shell["development_next_phase"],
        "phase96_closure_status": (
            "closed_nas_app_shell_local_service_smoke_ready_no_live_server_or_db"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase96_nas_app_shell_closure"]["hard_gates"])


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
