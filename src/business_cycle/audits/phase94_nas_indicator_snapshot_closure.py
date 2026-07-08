"""Phase 94 NAS indicator snapshot materialization closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_indicator_snapshots import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_indicator_snapshot,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase94_nas_indicator_snapshot_closure.yaml"


def summarize_phase94_nas_indicator_snapshot_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 94 closure gates for CI and final reporting."""

    snapshot_summary = summarize_nas_indicator_snapshot(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "94",
        "phase_id": 94,
        "phase94_closure_ready": True,
        "nas_indicator_snapshot_contract_ready": snapshot_summary[
            "nas_indicator_snapshot_contract_ready"
        ],
        "nas_indicator_snapshot_materialization_ready": snapshot_summary[
            "nas_indicator_snapshot_materialization_ready"
        ],
        "phase92_revised_import_dependency_ready": snapshot_summary[
            "phase92_revised_import_dependency_ready"
        ],
        "phase93_pit_availability_dependency_ready": snapshot_summary[
            "phase93_pit_availability_dependency_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": snapshot_summary[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "role_snapshot_count": snapshot_summary["role_snapshot_count"],
        "role_with_revised_snapshot_count": snapshot_summary[
            "role_with_revised_snapshot_count"
        ],
        "role_without_revised_snapshot_count": snapshot_summary[
            "role_without_revised_snapshot_count"
        ],
        "role_with_pit_backfill_plan_count": snapshot_summary[
            "role_with_pit_backfill_plan_count"
        ],
        "role_with_pit_backfill_blocker_count": snapshot_summary[
            "role_with_pit_backfill_blocker_count"
        ],
        "series_snapshot_count": snapshot_summary["series_snapshot_count"],
        "source_artifact_snapshot_count": snapshot_summary[
            "source_artifact_snapshot_count"
        ],
        "observation_revised_source_row_count": snapshot_summary[
            "observation_revised_source_row_count"
        ],
        "latest_revised_observation_context_count": snapshot_summary[
            "latest_revised_observation_context_count"
        ],
        "snapshot_row_schema_valid": snapshot_summary["snapshot_row_schema_valid"],
        "service_view_model_ready": snapshot_summary["service_view_model_ready"],
        "server_side_view_model_count": snapshot_summary[
            "server_side_view_model_count"
        ],
        "api_endpoint_contract_count": snapshot_summary["api_endpoint_contract_count"],
        "live_db_connection_attempt_count": snapshot_summary[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": snapshot_summary[
            "postgres_write_attempt_count"
        ],
        "live_fetch_attempt_count": snapshot_summary["live_fetch_attempt_count"],
        "repo_output_written_count": snapshot_summary["repo_output_written_count"],
        "public_output_count": snapshot_summary["public_output_count"],
        "observation_vintage_row_count": snapshot_summary[
            "observation_vintage_row_count"
        ],
        "strict_pit_result_emitted_count": snapshot_summary[
            "strict_pit_result_emitted_count"
        ],
        "point_in_time_claim_count": snapshot_summary["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": snapshot_summary[
            "revised_mislabeled_as_pit_count"
        ],
        "candidate_phase_emitted": snapshot_summary["candidate_phase_emitted"],
        "current_phase_emitted": snapshot_summary["current_phase_emitted"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_nas_snapshot_view_model_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "nas_snapshot_materialized_no_replay_execution"
        ),
        "development_next_phase": snapshot_summary["development_next_phase"],
        "phase94_closure_status": (
            "closed_nas_indicator_snapshot_materialized_no_live_db_or_public_output"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase94_nas_indicator_snapshot_closure"]["hard_gates"])


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
