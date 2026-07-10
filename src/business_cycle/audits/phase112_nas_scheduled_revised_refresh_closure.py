"""Phase 112 governed NAS scheduled revised refresh closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_scheduled_revised_refresh import (
    summarize_nas_scheduled_revised_refresh_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase112_nas_scheduled_revised_refresh_closure.yaml"


def summarize_phase112_nas_scheduled_revised_refresh_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase112_nas_scheduled_revised_refresh_closure"
    ]
    observed = payload["observed_live_acceptance"]
    implementation = summarize_nas_scheduled_revised_refresh_contract()
    progress = summarize_product_capability_progress()
    summary = {
        "phase": 112,
        "phase112_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_scheduled_revised_refresh_contract_ready": implementation[
            "nas_scheduled_revised_refresh_contract_ready"
        ],
        "scheduled_refresh_runner_ready": implementation[
            "scheduled_refresh_runner_ready"
        ],
        "source_health_status_ready": implementation["source_health_status_ready"],
        "dashboard_shell_ttl_cache_ready": implementation[
            "dashboard_shell_ttl_cache_ready"
        ],
        "live_refresh_accepted": observed["last_run_state"] == "succeeded"
        and observed["failed_series_count"] == 0,
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "app_image_reference": observed["app_image_reference"],
        "refresh_state": observed["refresh_state"],
        "last_run_state": observed["last_run_state"],
        "requested_series_count": observed["requested_series_count"],
        "completed_series_count": observed["completed_series_count"],
        "failed_series_count": observed["failed_series_count"],
        "source_artifact_row_count": observed["source_artifact_row_count"],
        "observation_revised_row_count": observed["observation_revised_row_count"],
        "observation_vintage_row_count": observed["observation_vintage_row_count"],
        "database_latest_observation_date": observed[
            "database_latest_observation_date"
        ],
        "dashboard_refresh_status_visible": observed[
            "dashboard_refresh_status_visible"
        ],
        "source_refresh_health_status": observed["source_refresh_health_status"],
        "live_fetch_attempt_count": observed["live_fetch_attempt_count"],
        "postgres_refresh_write_executed": observed[
            "postgres_refresh_write_executed"
        ],
        "candidate_phase_emitted": observed["candidate_phase_emitted"],
        "current_phase_emitted": observed["current_phase_emitted"],
        "prospective_registry_record_count": observed[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": observed[
            "real_registry_write_attempt_count"
        ],
        "secret_value_recorded": observed["secret_value_recorded"],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "runtime_behavior_change_count": 1,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 113,
        "phase112_closure_status": (
            "closed_scheduled_revised_refresh_and_source_health_live"
        ),
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary
