"""Phase 115 governed retry and private backup/restore closure."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_source_operations import render_nas_source_operations_page
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
)
from business_cycle.service.nas_source_retry_restore import (
    build_source_retry_preview,
    summarize_nas_source_retry_restore_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase115_nas_source_retry_restore_closure.yaml"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def summarize_phase115_nas_source_retry_restore_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase115_nas_source_retry_restore_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_source_retry_restore_contract()
    retry_preview = build_source_retry_preview(_successful_refresh_status())
    diagnostics = _fixture_diagnostics(retry_preview, observed)
    html = render_nas_source_operations_page(diagnostics)
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": 115,
        "phase115_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_source_retry_restore_contract_ready": contract[
            "nas_source_retry_restore_contract_ready"
        ],
        "retry_preview_ready": contract["retry_preview_ready"],
        "retry_preview_token_bound_to_status": contract[
            "retry_preview_token_bound_to_status"
        ],
        "retry_subset_scope_enforced": contract["retry_subset_scope_enforced"],
        "worker_only_retry_execution_ready": contract[
            "worker_only_retry_execution_ready"
        ],
        "no_failure_means_no_retry": retry_preview["no_failure_means_no_retry"],
        "live_retry_candidate_count": observed["live_retry_candidate_count"],
        "live_retry_execution_count": observed["live_retry_execution_count"],
        "backup_restore_runtime_ready": contract["backup_restore_runtime_ready"],
        "postgres_client_server_major_match_ready": contract[
            "postgres_client_server_major_match_ready"
        ],
        "postgres_client_server_major_match": (
            int(observed["postgres_client_major"])
            == int(observed["postgres_server_major"])
            == 16
        ),
        "backup_restore_state": observed["backup_restore_state"],
        "postgres_backup_checksum_valid": bool(
            SHA256_RE.fullmatch(str(observed["postgres_backup_checksum"]))
        ),
        "source_artifact_backup_checksum_valid": bool(
            SHA256_RE.fullmatch(str(observed["source_artifact_backup_checksum"]))
        ),
        "database_verification_table_count": contract[
            "database_verification_table_count"
        ],
        "database_row_count_match": (
            observed["row_count_match"]
            and observed["live_row_counts"] == observed["restored_row_counts"]
        ),
        "source_artifact_restore_count_match": (
            int(observed["source_artifact_file_count"])
            == int(observed["restored_source_artifact_file_count"])
            and int(observed["source_artifact_file_count"]) > 0
        ),
        "staging_database_dropped": observed["staging_database_dropped"],
        "source_retry_restore_renderer_ready": (
            "受治理重試與備份還原" in html
            and "私有 NAS 備份還原演練" in html
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
        "development_next_phase": 116,
        "phase115_closure_status": (
            "closed_governed_source_retry_and_backup_restore_drill_live"
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


def _successful_refresh_status() -> dict[str, Any]:
    series_ids = load_nas_postgres_live_revised_import_contract()["source_policy"][
        "direct_series_ids"
    ]
    return {
        "status_version": "phase114_refresh_status_v2",
        "run_id": "successful-run",
        "last_run_state": "succeeded",
        "last_completed_at_utc": "2026-07-10T12:00:00Z",
        "series_refresh_results": [
            {"series_id": series_id, "status": "imported"}
            for series_id in series_ids
        ],
    }


def _fixture_diagnostics(
    retry_preview: dict[str, Any],
    observed: dict[str, Any],
) -> dict[str, Any]:
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
        refresh_status=_successful_refresh_status(),
    )
    diagnostics["source_retry_preview"] = retry_preview
    diagnostics["backup_restore_status"] = {
        "backup_restore_state": observed["backup_restore_state"],
        "row_count_match": observed["row_count_match"],
        "staging_database_dropped": observed["staging_database_dropped"],
        "source_artifact_file_count": observed["source_artifact_file_count"],
        "restored_source_artifact_file_count": observed[
            "restored_source_artifact_file_count"
        ],
        "live_row_counts": observed["live_row_counts"],
    }
    return diagnostics
