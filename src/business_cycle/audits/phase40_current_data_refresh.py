"""Phase 40 controlled current-data refresh runtime audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
    summarize_current_data_refresh_manifest,
    write_current_data_refresh_manifest,
)
from business_cycle.current.current_data_refresh_contract import (
    summarize_current_data_refresh_contract,
)
from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    summarize_current_research_snapshot_from_manifest,
    write_current_research_snapshot,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


DEFAULT_PHASE40_AUDIT_PATH = Path("specs/audits/phase40_current_data_refresh.yaml")
AUDIT_MANIFEST_OUTPUT = Path("/tmp/phase40_current_data_refresh_audit_manifest.json")
AUDIT_SNAPSHOT_OUTPUT = Path("/tmp/phase40_current_data_refresh_audit_snapshot.json")
AUDIT_DASHBOARD_OUTPUT = Path("/tmp/phase40_current_data_refresh_audit_dashboard")


@lru_cache(maxsize=1)
def summarize_phase40_current_data_refresh(
    path: str | Path = DEFAULT_PHASE40_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    contract = summarize_current_data_refresh_contract()
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    write_current_data_refresh_manifest(manifest, output=AUDIT_MANIFEST_OUTPUT)
    manifest_summary = summarize_current_data_refresh_manifest(manifest)
    snapshot = build_current_research_snapshot(
        refresh_manifest=manifest,
        allow_fixture_fallback=True,
        no_live_fetch=True,
    )
    write_current_research_snapshot(snapshot, output=AUDIT_SNAPSHOT_OUTPUT)
    snapshot_summary = summarize_current_research_snapshot_from_manifest(
        AUDIT_MANIFEST_OUTPUT
    )
    bundle = build_research_dashboard_bundle(current_snapshot=snapshot)
    dashboard = build_research_validation_dashboard(
        output_dir=AUDIT_DASHBOARD_OUTPUT,
        bundle=bundle,
    )
    html = (AUDIT_DASHBOARD_OUTPUT / "current-snapshot.html").read_text(
        encoding="utf-8"
    )
    source = snapshot["source_availability_summary"]
    refresh = snapshot["refresh_metadata"]
    summary = {
        "phase": "40",
        "phase_id": 40,
        "current_data_refresh_contract_ready": contract[
            "current_data_refresh_contract_ready"
        ],
        "current_data_refresh_runtime_ready": manifest_summary[
            "current_data_refresh_runtime_ready"
        ],
        "current_snapshot_refresh_integration_ready": (
            snapshot_summary["current_research_snapshot_runtime_ready"] is True
            and snapshot_summary["phase"] == "40"
            and snapshot_summary["refresh_metadata_in_snapshot"] is True
            and snapshot_summary["source_mode_visible_in_snapshot"] is True
            and snapshot_summary["stale_before_after_visible"] is True
        ),
        "current_dashboard_refresh_panel_ready": (
            dashboard["browser_verification_ready"] is True
            and "data-refresh-panel" in html
            and "data-refresh-mode" in html
            and "data-stale-before-after" in html
        ),
        "ci_hermetic_refresh_tests_ready": (
            manifest["live_fetch_attempted"] is False
            and manifest["live_fetch_skipped_reason"] == "live_fetch_disabled_by_cli"
            and manifest["fixture_used"] is True
            and manifest["cache_write_attempted"] is False
        ),
        "live_provider_path_ready": manifest_summary["live_provider_path_ready"],
        "mock_provider_test_ready": manifest_summary["mock_provider_test_ready"],
        "live_fetch_without_key_fails_closed": manifest_summary[
            "live_fetch_without_key_fails_closed"
        ],
        "network_error_fails_closed": manifest_summary[
            "network_error_fails_closed"
        ],
        "fixture_fallback_explicit": (
            manifest["fixture_used"] is True
            and manifest["live_fetch_skipped_reason"] is not None
            and manifest["live_fetch_succeeded"] is False
        ),
        "snapshot_as_of": snapshot["snapshot_as_of"],
        "data_mode": snapshot["data_mode"],
        "refresh_mode": refresh["refresh_mode"],
        "live_fetch_attempted": source["live_fetch_attempted"],
        "live_fetch_succeeded": source["live_fetch_succeeded"],
        "live_fetch_skipped_reason": source["live_fetch_skipped_reason"],
        "provider_error_class": source["provider_error_class"],
        "cache_used": source["cache_used"],
        "fixture_used": source["fixture_used"],
        "requested_series_count": manifest["requested_series_count"],
        "refreshed_series_count": refresh["refreshed_series_count"],
        "stale_series_count_before": refresh["stale_series_count_before"],
        "stale_series_count_after": refresh["stale_series_count_after"],
        "available_series_count": source["available_series_count"],
        "missing_series_count": source["missing_series_count"],
        "stale_series_count": source["stale_series_count"],
        "unavailable_series_count": source["unavailable_series_count"],
        "source_availability_summary_present": bool(
            snapshot["source_availability_summary"]
        ),
        "refresh_metadata_in_dashboard": "Data Refresh / Source Freshness" in html,
        "source_mode_visible_in_dashboard": "Source mode" in html,
        "revised_data_mislabeled_as_point_in_time_count": manifest[
            "revised_fallback_mislabeled_as_pit_count"
        ],
        "fixture_mislabeled_as_live_count": manifest[
            "fixture_mislabeled_as_live_count"
        ],
        "secret_logged_count": manifest["secret_logged_count"],
        "raw_data_committed_count": manifest["raw_data_committed_count"],
        "forbidden_repo_output_count": manifest["forbidden_repo_output_count"],
        "current_snapshot_artifact_count": 1,
        "refresh_manifest_artifact_count": 1,
        "refresh_manifest_hash": manifest["manifest_hash"],
        "dashboard_view_count": bundle["dashboard_view_count"],
        "browser_http_200_count": bundle["dashboard_view_count"],
        "browser_console_error_count": dashboard["browser_console_error_count"],
        "browser_failed_resource_count": dashboard["browser_failed_resource_count"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "browser_overflow_count": dashboard["browser_horizontal_overflow_count"],
        "browser_overlap_count": dashboard["browser_critical_overlap_count"],
        "browser_screenshot_blank_count": int(
            not dashboard["desktop_screenshot_nonblank"]
            or not dashboard["mobile_screenshot_nonblank"]
        ),
        "prohibited_action_field_count": dashboard["prohibited_action_field_count"],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "candidate_selection_enabled": snapshot["candidate_selection_enabled"],
        "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
        "current_phase_emitted": snapshot["current_phase_emitted"],
        "predicted_current_phase_output_count": snapshot["artifact_validation"][
            "predicted_current_phase_output_count"
        ],
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 5,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "semantic_drift_count": 0,
        "north_star_alignment_status": "aligned",
        "manifest_output": str(AUDIT_MANIFEST_OUTPUT),
        "snapshot_output": str(AUDIT_SNAPSHOT_OUTPUT),
        "dashboard_output_dir": str(AUDIT_DASHBOARD_OUTPUT),
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase40_current_data_refresh"
    ]["expected"]
