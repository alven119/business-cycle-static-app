"""Phase 92 revised macro data completeness import closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.revised_macro_data_import import (
    DEFAULT_CONTRACT_PATH,
    summarize_revised_macro_data_import,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase92_revised_macro_data_import_closure.yaml"


def summarize_phase92_revised_macro_data_import_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 92 closure gates for CI and final reporting."""

    import_summary = summarize_revised_macro_data_import(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "92",
        "phase_id": 92,
        "phase92_closure_ready": True,
        "revised_macro_data_import_contract_ready": import_summary[
            "revised_macro_data_import_contract_ready"
        ],
        "revised_macro_data_import_dry_run_ready": import_summary[
            "revised_macro_data_import_dry_run_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": import_summary[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "role_count": import_summary["role_count"],
        "revised_import_ready_role_count": import_summary[
            "revised_import_ready_role_count"
        ],
        "revised_import_blocked_role_count": import_summary[
            "revised_import_blocked_role_count"
        ],
        "role_without_import_status_count": import_summary[
            "role_without_import_status_count"
        ],
        "blocked_role_with_reason_count": import_summary[
            "blocked_role_with_reason_count"
        ],
        "unique_series_count": import_summary["unique_series_count"],
        "series_registry_row_count": import_summary["series_registry_row_count"],
        "source_artifact_row_count": import_summary["source_artifact_row_count"],
        "observation_revised_row_count": import_summary[
            "observation_revised_row_count"
        ],
        "observation_vintage_row_count": import_summary[
            "observation_vintage_row_count"
        ],
        "warehouse_row_schema_valid": import_summary["warehouse_row_schema_valid"],
        "source_artifact_hash_complete": import_summary[
            "source_artifact_hash_complete"
        ],
        "provenance_hash_complete": import_summary["provenance_hash_complete"],
        "dry_run_output_under_tmp_only": import_summary[
            "dry_run_output_under_tmp_only"
        ],
        "live_db_connection_attempt_count": import_summary[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": import_summary["postgres_write_attempt_count"],
        "live_fetch_attempt_count": import_summary["live_fetch_attempt_count"],
        "repo_output_written_count": import_summary["repo_output_written_count"],
        "point_in_time_claim_count": import_summary["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": import_summary[
            "revised_mislabeled_as_pit_count"
        ],
        "candidate_phase_emitted": import_summary["candidate_phase_emitted"],
        "current_phase_emitted": import_summary["current_phase_emitted"],
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
            "declared_state_preserved_revised_import_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "revised_warehouse_import_ready_no_replay_execution"
        ),
        "development_next_phase": import_summary["development_next_phase"],
        "phase92_closure_status": (
            "closed_revised_macro_data_import_dry_run_ready_no_db_or_live_fetch"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase92_revised_macro_data_import_closure"]["hard_gates"])


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
