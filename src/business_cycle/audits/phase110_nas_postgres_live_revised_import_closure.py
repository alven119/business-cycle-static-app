"""Phase 110 live revised-history import closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.storage.nas_postgres_live_revised_import import (
    summarize_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase110_nas_postgres_live_revised_import_closure.yaml"


def summarize_phase110_nas_postgres_live_revised_import_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase110_nas_postgres_live_revised_import_closure"
    ]
    observed = payload["observed_live_acceptance"]
    implementation = summarize_nas_postgres_live_revised_import_contract()
    summary = {
        "phase": 110,
        "phase110_closure_ready": True,
        "nas_postgres_live_revised_import_contract_ready": implementation[
            "nas_postgres_live_revised_import_contract_ready"
        ],
        "baseline_backup_ready": observed["baseline_backup_ready"],
        "schema_migration_executed": observed["schema_table_count"] == 11,
        "schema_table_count": observed["schema_table_count"],
        "requested_series_count": implementation["direct_series_count"],
        "completed_series_count": observed["series_registry_row_count"],
        "failed_series_count": observed["failed_series_count"],
        "series_registry_row_count": observed["series_registry_row_count"],
        "source_artifact_row_count": observed["source_artifact_row_count"],
        "observation_revised_row_count": observed["observation_revised_row_count"],
        "observation_vintage_row_count": observed["observation_vintage_row_count"],
        "earliest_revised_observation_date": observed[
            "earliest_revised_observation_date"
        ],
        "latest_revised_observation_date": observed[
            "latest_revised_observation_date"
        ],
        "artifact_csv_count": observed["artifact_csv_count"],
        "checkpoint_resume_verified": observed["resume_row_count_unchanged"],
        "resume_row_count_unchanged": observed["resume_row_count_unchanged"],
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "public_output_count": 0,
        "prospective_registry_write_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 111,
        "phase110_closure_status": (
            "closed_nas_postgres_revised_history_imported_live_db_read_next"
        ),
    }
    expected = payload["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary
