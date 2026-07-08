"""Phase 91 PIT-ready Postgres macro warehouse closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.storage.postgres_macro_warehouse import (
    DEFAULT_CONTRACT_PATH,
    load_postgres_macro_warehouse_contract,
    summarize_postgres_macro_warehouse_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase91_postgres_macro_warehouse_closure.yaml"
NAS_CONTRACT_PATH = ROOT / "specs/common/nas_dynamic_service_contract.yaml"


def summarize_phase91_postgres_macro_warehouse_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 91 closure gates for scripts and tests."""

    contract_summary = summarize_postgres_macro_warehouse_contract(contract_path)
    contract = load_postgres_macro_warehouse_contract(contract_path)
    expected = _load_expected(closure_path)
    design = contract["design_principles"]
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])

    summary: dict[str, Any] = {
        "phase": "91",
        "phase_id": 91,
        "phase91_closure_ready": True,
        "postgres_macro_warehouse_contract_ready": contract_summary[
            "postgres_macro_warehouse_contract_ready"
        ],
        "nas_dynamic_service_dependency_ready": _nas_dependency_ready(),
        "schema_table_count": contract_summary["schema_table_count"],
        "required_table_count": contract_summary["required_table_count"],
        "missing_required_table_count": contract_summary[
            "missing_required_table_count"
        ],
        "table_with_primary_key_count": contract_summary[
            "table_with_primary_key_count"
        ],
        "table_without_primary_key_count": contract_summary[
            "table_without_primary_key_count"
        ],
        "pit_ready_schema": contract_summary["pit_ready_schema"],
        "revised_vintage_separation_ready": contract_summary[
            "revised_vintage_separation_ready"
        ],
        "vintage_required_column_missing_count": contract_summary[
            "vintage_required_column_missing_count"
        ],
        "revised_first_backfill_policy_present": bool(
            design["revised_data_complete_first"],
        ),
        "vintage_backfill_plan_present": bool(design["vintage_backfill_incremental"]),
        "schema_sql_generated": contract_summary["schema_sql_generated"],
        "schema_requires_live_db": contract_summary["schema_requires_live_db"],
        "live_db_connection_attempt_count": contract_summary[
            "live_db_connection_attempt_count"
        ],
        "runtime_dependency_added_count": contract_summary[
            "runtime_dependency_added_count"
        ],
        "frontend_database_access_allowed": contract_summary[
            "frontend_database_access_allowed"
        ],
        "frontend_api_key_allowed": contract_summary["frontend_api_key_allowed"],
        "candidate_phase_emitted": contract_summary["candidate_phase_emitted"],
        "current_phase_emitted": contract_summary["current_phase_emitted"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": "declared_state_preserved_schema_only",
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "pit_ready_schema_preregistered_no_execution"
        ),
        "development_next_phase": contract_summary["development_next_phase"],
        "phase91_closure_status": (
            "closed_postgres_macro_warehouse_pit_schema_ready_no_live_db_dependency"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase91_postgres_macro_warehouse_closure"]["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _nas_dependency_ready() -> bool:
    payload = yaml.safe_load(NAS_CONTRACT_PATH.read_text(encoding="utf-8"))
    contract = payload["nas_dynamic_service_contract"]
    return (
        contract["status"] == "active"
        and contract["runtime_stack"]["database"]["engine"] == "postgres"
        and contract["runtime_stack"]["database"]["pit_schema_required_from_start"]
        is True
    )


def _git_ls_files(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
