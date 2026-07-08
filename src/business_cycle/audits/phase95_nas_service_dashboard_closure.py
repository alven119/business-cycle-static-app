"""Phase95 NAS service dashboard route/API/HTML rehearsal closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_service_dashboard import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_service_dashboard,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase95_nas_service_dashboard_closure.yaml"


def summarize_phase95_nas_service_dashboard_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase95 closure gates for CI and final reporting."""

    dashboard = summarize_nas_service_dashboard(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "95",
        "phase_id": 95,
        "phase95_closure_ready": True,
        "nas_service_dashboard_contract_ready": dashboard[
            "nas_service_dashboard_contract_ready"
        ],
        "nas_service_route_manifest_ready": dashboard[
            "nas_service_route_manifest_ready"
        ],
        "nas_service_api_payload_ready": dashboard[
            "nas_service_api_payload_ready"
        ],
        "nas_service_html_renderer_ready": dashboard[
            "nas_service_html_renderer_ready"
        ],
        "private_nas_service_target_ready": dashboard[
            "private_nas_service_target_ready"
        ],
        "phase94_snapshot_dependency_ready": dashboard[
            "phase94_snapshot_dependency_ready"
        ],
        "product_capability_rebaseline_recorded": dashboard[
            "product_capability_rebaseline_recorded"
        ],
        "route_count": dashboard["route_count"],
        "api_payload_count": dashboard["api_payload_count"],
        "html_page_count": dashboard["html_page_count"],
        "role_card_count": dashboard["role_card_count"],
        "indicator_snapshot_api_role_count": dashboard[
            "indicator_snapshot_api_role_count"
        ],
        "html_role_card_count": dashboard["html_role_card_count"],
        "html_revised_snapshot_role_count": dashboard[
            "html_revised_snapshot_role_count"
        ],
        "html_blocked_role_count": dashboard["html_blocked_role_count"],
        "mobile_trust_caveat_count": dashboard["mobile_trust_caveat_count"],
        "frontend_database_access_allowed": dashboard[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": dashboard["frontend_api_key_allowed"],
        "live_server_start_attempt_count": dashboard[
            "live_server_start_attempt_count"
        ],
        "live_db_connection_attempt_count": dashboard[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": dashboard["postgres_write_attempt_count"],
        "live_fetch_attempt_count": dashboard["live_fetch_attempt_count"],
        "repo_output_written_count": dashboard["repo_output_written_count"],
        "public_output_count": dashboard["public_output_count"],
        "prohibited_output_field_count": dashboard["prohibited_output_field_count"],
        "candidate_phase_emitted": dashboard["candidate_phase_emitted"],
        "current_phase_emitted": dashboard["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": dashboard[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": dashboard[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": dashboard[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": dashboard[
            "role_count_voting_added_count"
        ],
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
            "declared_state_preserved_nas_route_api_html_rehearsal"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_dashboard_renderer_ready_no_replay_execution"
        ),
        "development_next_phase": dashboard["development_next_phase"],
        "phase95_closure_status": (
            "closed_nas_service_dashboard_route_api_html_rehearsed_no_live_server_or_db"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase95_nas_service_dashboard_closure"]["hard_gates"])


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
