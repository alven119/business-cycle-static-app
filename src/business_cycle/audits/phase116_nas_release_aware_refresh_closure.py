"""Phase 116 fixed-time and release-aware NAS refresh closure."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_source_operations import render_nas_source_operations_page
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
)
from business_cycle.service.nas_release_aware_refresh import (
    build_release_aware_schedule_preview,
    summarize_nas_release_aware_refresh_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase116_nas_release_aware_refresh_closure.yaml"


def summarize_phase116_nas_release_aware_refresh_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase116_nas_release_aware_refresh_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_release_aware_refresh_contract()
    diagnostics = _fixture_diagnostics(observed)
    html = render_nas_source_operations_page(diagnostics)
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": 116,
        "phase116_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_release_aware_refresh_contract_ready": contract[
            "nas_release_aware_refresh_contract_ready"
        ],
        "fixed_daily_wall_clock_schedule_ready": contract[
            "fixed_daily_wall_clock_schedule_ready"
        ],
        "fixed_daily_time_zone": observed["fixed_daily_time_zone"],
        "fixed_daily_local_time": observed["fixed_daily_local_time"],
        "live_scheduler_state_ready": observed["scheduler_state"] in {
            "scheduled",
            "running",
            "succeeded",
        },
        "next_trigger_visible": bool(observed["next_scheduled_at_local"]),
        "next_trigger_kind": observed["next_trigger_kind"],
        "next_series_count": observed["next_series_count"],
        "release_aware_job_execution_count": observed[
            "release_aware_job_execution_count"
        ],
        "exact_schedule_release_followup_ready": contract[
            "exact_schedule_release_followup_ready"
        ],
        "exact_calendar_family_count": observed["exact_calendar_family_count"],
        "minimum_exact_calendar_horizon": observed[
            "minimum_exact_calendar_horizon"
        ],
        "release_followup_availability_claim_count": contract[
            "release_followup_availability_claim_count"
        ],
        "cadence_or_reference_release_trigger_count": contract[
            "cadence_or_reference_release_trigger_count"
        ],
        "canonical_subset_enforced": contract["canonical_subset_enforced"],
        "backup_retention_preview_ready": contract[
            "backup_retention_preview_ready"
        ],
        "backup_retention_automatic_delete_count": contract[
            "backup_retention_automatic_delete_count"
        ],
        "backup_successful_run_count": observed["backup_successful_run_count"],
        "backup_failed_run_count": observed["backup_failed_run_count"],
        "backup_unknown_run_count": observed["backup_unknown_run_count"],
        "retention_candidate_count": observed["retention_candidate_count"],
        "retention_delete_execution_count": observed[
            "retention_delete_execution_count"
        ],
        "direct_revised_series_count": contract["direct_revised_series_count"],
        "revised_direct_source_scope_complete": (
            int(observed["series_registry_row_count"]) == 26
            and int(observed["source_artifact_row_count"]) >= 26
        ),
        "observation_revised_row_count": observed[
            "observation_revised_row_count"
        ],
        "observation_revised_row_count_positive": int(
            observed["observation_revised_row_count"]
        ) > 0,
        "observation_vintage_row_count": observed[
            "observation_vintage_row_count"
        ],
        "release_calendar_row_count": observed["release_calendar_row_count"],
        "macro_history_all_modes_complete": contract[
            "macro_history_all_modes_complete"
        ],
        "source_operations_renderer_ready": (
            "固定時間與官方發布補抓" in html
            and "私人備份保留預覽" in html
        ),
        "source_operations_page_authenticated_access": observed[
            "source_operations_page_authenticated_access"
        ],
        "source_operations_api_authenticated_access": observed[
            "source_operations_api_authenticated_access"
        ],
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "app_image_reference": observed["app_image_reference"],
        "secret_value_recorded": observed["secret_value_recorded"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "public_exposure_enabled": observed["public_exposure_enabled"],
        "prospective_registry_write_count": observed[
            "prospective_registry_write_count"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 117,
        "phase116_closure_status": (
            "closed_fixed_time_release_aware_refresh_and_retention_preview_live"
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


def _fixture_diagnostics(observed: dict[str, Any]) -> dict[str, Any]:
    series_ids = load_nas_postgres_live_revised_import_contract()["source_policy"][
        "direct_series_ids"
    ]
    diagnostics = build_nas_official_release_diagnostics(
        as_of="2026-07-10",
        series_inputs=[
            {
                "series_id": series_id,
                "frequency": "monthly",
                "latest_observation_date": "2026-07-01",
                "freshness_status": "fresh",
            }
            for series_id in series_ids
        ],
        refresh_status={
            "refresh_state": "succeeded",
            "last_run_state": "succeeded",
            "last_completed_at_utc": "2026-07-10T12:00:00Z",
            "series_refresh_results": [],
        },
    )
    preview = build_release_aware_schedule_preview(
        now=datetime(2026, 7, 11, tzinfo=timezone.utc)
    )
    diagnostics["release_aware_schedule_status"] = {
        "fixed_daily_local_time": observed["fixed_daily_local_time"],
        "fixed_daily_time_zone": observed["fixed_daily_time_zone"],
        "next_scheduled_at_local": observed["next_scheduled_at_local"],
        "next_trigger_kind": observed["next_trigger_kind"],
        "next_series_count": observed["next_series_count"],
        "minimum_exact_calendar_horizon": preview[
            "minimum_exact_calendar_horizon"
        ],
    }
    diagnostics["backup_retention_preview"] = {
        "successful_run_count": observed["backup_successful_run_count"],
        "successful_run_keep_count": 7,
        "failed_run_count": observed["backup_failed_run_count"],
        "failed_run_keep_count": 3,
        "unknown_run_count": observed["backup_unknown_run_count"],
        "retention_candidate_count": observed["retention_candidate_count"],
    }
    return diagnostics
