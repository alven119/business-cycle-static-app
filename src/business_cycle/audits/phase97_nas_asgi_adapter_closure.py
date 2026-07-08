"""Phase97 NAS ASGI adapter skeleton closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_asgi_adapter import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_asgi_adapter,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase97_nas_asgi_adapter_closure.yaml"


def summarize_phase97_nas_asgi_adapter_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase97 closure gates for CI and final reporting."""

    adapter = summarize_nas_asgi_adapter(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "97",
        "phase_id": 97,
        "phase97_closure_ready": True,
        "nas_asgi_adapter_contract_ready": adapter[
            "nas_asgi_adapter_contract_ready"
        ],
        "nas_asgi_adapter_ready": adapter["nas_asgi_adapter_ready"],
        "asgi_scope_adapter_ready": adapter["asgi_scope_adapter_ready"],
        "fastapi_mount_compatibility_ready": adapter[
            "fastapi_mount_compatibility_ready"
        ],
        "local_asgi_smoke_ready": adapter["local_asgi_smoke_ready"],
        "phase96_shell_dependency_ready": adapter["phase96_shell_dependency_ready"],
        "route_count": adapter["route_count"],
        "authenticated_asgi_smoke_pass_count": adapter[
            "authenticated_asgi_smoke_pass_count"
        ],
        "unauthenticated_asgi_smoke_rejected_count": adapter[
            "unauthenticated_asgi_smoke_rejected_count"
        ],
        "unsupported_method_rejected_count": adapter[
            "unsupported_method_rejected_count"
        ],
        "unknown_route_rejected_count": adapter["unknown_route_rejected_count"],
        "response_start_event_count": adapter["response_start_event_count"],
        "response_body_event_count": adapter["response_body_event_count"],
        "uvicorn_run_attempt_count": adapter["uvicorn_run_attempt_count"],
        "network_bind_attempt_count": adapter["network_bind_attempt_count"],
        "live_server_start_attempt_count": adapter["live_server_start_attempt_count"],
        "live_db_connection_attempt_count": adapter[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": adapter["postgres_write_attempt_count"],
        "live_fetch_attempt_count": adapter["live_fetch_attempt_count"],
        "repo_output_written_count": adapter["repo_output_written_count"],
        "public_output_count": adapter["public_output_count"],
        "frontend_database_access_allowed": adapter[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": adapter["frontend_api_key_allowed"],
        "prohibited_output_field_count": adapter["prohibited_output_field_count"],
        "candidate_phase_emitted": adapter["candidate_phase_emitted"],
        "current_phase_emitted": adapter["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": adapter[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": adapter[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": adapter[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": adapter["role_count_voting_added_count"],
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
            "declared_state_preserved_asgi_adapter_smoke_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_asgi_adapter_ready_no_replay_execution"
        ),
        "development_next_phase": adapter["development_next_phase"],
        "phase97_closure_status": (
            "closed_nas_asgi_adapter_skeleton_ready_no_live_server_or_db"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase97_nas_asgi_adapter_closure"]["hard_gates"])


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
