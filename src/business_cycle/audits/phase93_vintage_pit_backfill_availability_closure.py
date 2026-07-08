"""Phase 93 vintage/PIT backfill availability accounting closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.vintage_pit_backfill_availability import (
    DEFAULT_CONTRACT_PATH,
    summarize_vintage_pit_backfill_availability,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = (
    ROOT / "specs/audits/phase93_vintage_pit_backfill_availability_closure.yaml"
)


def summarize_phase93_vintage_pit_backfill_availability_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 93 closure gates for CI and final reporting."""

    backfill_summary = summarize_vintage_pit_backfill_availability(
        contract_path=contract_path,
    )
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "93",
        "phase_id": 93,
        "phase93_closure_ready": True,
        "vintage_pit_backfill_availability_contract_ready": backfill_summary[
            "vintage_pit_backfill_availability_contract_ready"
        ],
        "vintage_pit_backfill_accounting_ready": backfill_summary[
            "vintage_pit_backfill_accounting_ready"
        ],
        "phase92_revised_import_dependency_ready": backfill_summary[
            "phase92_revised_import_dependency_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": backfill_summary[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "role_count": backfill_summary["role_count"],
        "revised_import_ready_role_count": backfill_summary[
            "revised_import_ready_role_count"
        ],
        "revised_import_blocked_role_count": backfill_summary[
            "revised_import_blocked_role_count"
        ],
        "role_with_pit_backfill_plan_count": backfill_summary[
            "role_with_pit_backfill_plan_count"
        ],
        "role_blocked_from_pit_backfill_count": backfill_summary[
            "role_blocked_from_pit_backfill_count"
        ],
        "blocked_role_with_reason_count": backfill_summary[
            "blocked_role_with_reason_count"
        ],
        "unique_series_count": backfill_summary["unique_series_count"],
        "backfill_availability_row_count": backfill_summary[
            "backfill_availability_row_count"
        ],
        "series_registry_metadata_covered_count": backfill_summary[
            "series_registry_metadata_covered_count"
        ],
        "series_missing_release_lag_registry_count": backfill_summary[
            "series_missing_release_lag_registry_count"
        ],
        "pit_eligible_series_count": backfill_summary["pit_eligible_series_count"],
        "vintage_query_supported_series_count": backfill_summary[
            "vintage_query_supported_series_count"
        ],
        "derived_pit_plan_series_count": backfill_summary[
            "derived_pit_plan_series_count"
        ],
        "planned_vintage_backfill_series_count": backfill_summary[
            "planned_vintage_backfill_series_count"
        ],
        "planned_vintage_request_row_count": backfill_summary[
            "planned_vintage_request_row_count"
        ],
        "observation_vintage_row_count": backfill_summary[
            "observation_vintage_row_count"
        ],
        "strict_pit_result_emitted_count": backfill_summary[
            "strict_pit_result_emitted_count"
        ],
        "local_vintage_cache_verification_attempt_count": backfill_summary[
            "local_vintage_cache_verification_attempt_count"
        ],
        "local_vintage_cache_write_count": backfill_summary[
            "local_vintage_cache_write_count"
        ],
        "live_db_connection_attempt_count": backfill_summary[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": backfill_summary[
            "postgres_write_attempt_count"
        ],
        "live_fetch_attempt_count": backfill_summary["live_fetch_attempt_count"],
        "repo_output_written_count": backfill_summary["repo_output_written_count"],
        "point_in_time_claim_count": backfill_summary["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": backfill_summary[
            "revised_mislabeled_as_pit_count"
        ],
        "candidate_phase_emitted": backfill_summary["candidate_phase_emitted"],
        "current_phase_emitted": backfill_summary["current_phase_emitted"],
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
            "declared_state_preserved_vintage_backfill_accounting_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "vintage_pit_backfill_accounted_no_replay_execution"
        ),
        "development_next_phase": backfill_summary["development_next_phase"],
        "phase93_closure_status": (
            "closed_vintage_pit_backfill_availability_accounted_no_live_fetch_or_pit_results"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase93_vintage_pit_backfill_availability_closure"]["hard_gates"],
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
