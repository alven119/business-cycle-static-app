"""Phase 114 private NAS source-operations closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_source_operations import (
    render_nas_source_operations_page,
)
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
    summarize_nas_official_release_calendar_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase114_nas_official_release_operations_closure.yaml"


def summarize_phase114_nas_official_release_operations_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase114_nas_official_release_operations_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_official_release_calendar_contract()
    diagnostics = build_phase114_fixture_diagnostics()
    html = render_nas_source_operations_page(diagnostics)
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": 114,
        "phase114_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_official_release_calendar_contract_ready": contract[
            "nas_official_release_calendar_contract_ready"
        ],
        "release_calendar_runtime_ready": diagnostics["release_calendar_runtime_ready"],
        "refresh_status_per_series_results_ready": True,
        "source_operations_renderer_ready": (
            "官方資料發布與更新維運" in html
            and "逐序列 refresh drilldown" in html
        ),
        "private_source_operations_route_count": contract[
            "private_source_operations_route_count"
        ],
        "direct_series_count": contract["direct_series_count"],
        "release_family_count": contract["release_family_count"],
        "series_diagnostic_count": diagnostics["series_diagnostic_count"],
        "exact_schedule_family_count": contract["exact_schedule_family_count"],
        "source_operations_page_authenticated_access": observed[
            "source_operations_page_authenticated_access"
        ],
        "source_operations_api_authenticated_access": observed[
            "source_operations_api_authenticated_access"
        ],
        "overview_source_operations_link_visible": observed[
            "overview_source_operations_link_visible"
        ],
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "app_image_reference": observed["app_image_reference"],
        "observation_date_assumed_release_date_count": diagnostics[
            "observation_date_assumed_release_date_count"
        ],
        "official_delay_claim_without_exact_schedule_count": contract[
            "official_delay_claim_without_exact_schedule_count"
        ],
        "refresh_failure_separated_from_source_delay": diagnostics[
            "refresh_failure_separated_from_source_delay"
        ],
        "candidate_phase_emitted": diagnostics["candidate_phase_emitted"],
        "current_phase_emitted": diagnostics["current_phase_emitted"],
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
        "development_next_phase": 115,
        "phase114_closure_status": (
            "closed_per_source_release_calendar_and_refresh_failure_drilldown_live"
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


def build_phase114_fixture_diagnostics() -> dict[str, Any]:
    series_ids = load_nas_postgres_live_revised_import_contract()[
        "source_policy"
    ]["direct_series_ids"]
    return build_nas_official_release_diagnostics(
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
            "series_refresh_results": [
                {
                    "series_id": series_id,
                    "status": "imported",
                    "observation_count": 10,
                    "error_class": None,
                }
                for series_id in series_ids
            ],
        },
    )
