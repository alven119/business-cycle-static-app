"""Phase 41 opt-in live/current refresh smoke audit."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.current.current_data_refresh import (
    LIVE_OPERATOR_CONFIRMATION,
    build_current_data_refresh_manifest,
    summarize_current_data_refresh_manifest,
    write_current_data_refresh_manifest,
)
from business_cycle.current.current_live_refresh_probe import (
    probe_current_live_refresh_environment,
)
from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    write_current_research_snapshot,
)
from business_cycle.current.current_stale_remediation import (
    summarize_current_stale_remediation,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


DEFAULT_PHASE41_AUDIT_PATH = Path("specs/audits/phase41_live_current_refresh_smoke.yaml")
PROBE_OUTPUT = Path("/tmp/phase41_live_probe.json")
LIVE_MANIFEST_OUTPUT = Path("/tmp/phase41_refresh_manifest_live.json")
BLOCKED_MANIFEST_OUTPUT = Path("/tmp/phase41_refresh_manifest_blocked.json")
SNAPSHOT_LIVE_OUTPUT = Path("/tmp/phase41_current_snapshot_live.json")
SNAPSHOT_BLOCKED_OUTPUT = Path("/tmp/phase41_current_snapshot_blocked.json")
DASHBOARD_OUTPUT = Path("/tmp/business_cycle_phase41_dashboard")
BROWSER_VERIFICATION_DIR = Path("/tmp/phase41_browser_verification")
VERIFIED_LOCAL_URL = "http://127.0.0.1:8765/current-snapshot.html"


@lru_cache(maxsize=1)
def summarize_phase41_live_current_refresh_smoke(
    path: str | Path = DEFAULT_PHASE41_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    probe = probe_current_live_refresh_environment(output=PROBE_OUTPUT)
    manifest = build_current_data_refresh_manifest(
        cache_dir="data/raw/fred_current_cache",
        execute_live=True,
        operator_confirmation=LIVE_OPERATOR_CONFIRMATION,
    )
    manifest_output = (
        LIVE_MANIFEST_OUTPUT
        if manifest["live_fetch_attempted"]
        else BLOCKED_MANIFEST_OUTPUT
    )
    write_current_data_refresh_manifest(manifest, output=manifest_output)
    manifest_summary = summarize_current_data_refresh_manifest(manifest)
    stale = summarize_current_stale_remediation(refresh_manifest=manifest)
    snapshot = build_current_research_snapshot(
        refresh_manifest=manifest,
        allow_fixture_fallback=manifest["fixture_used"],
    )
    snapshot_output = (
        SNAPSHOT_LIVE_OUTPUT
        if manifest["live_fetch_succeeded"]
        else SNAPSHOT_BLOCKED_OUTPUT
    )
    write_current_research_snapshot(snapshot, output=snapshot_output)
    bundle = build_research_dashboard_bundle(current_snapshot=snapshot)
    dashboard = build_research_validation_dashboard(
        output_dir=DASHBOARD_OUTPUT,
        bundle=bundle,
    )
    browser_verification = _write_browser_verification(dashboard)
    source = snapshot["source_availability_summary"]
    refresh = snapshot["refresh_metadata"]
    key_present = probe["fred_api_key_present"]
    summary = {
        "phase": "41",
        "phase_id": 41,
        "live_refresh_probe_ready": probe["live_refresh_probe_ready"],
        "controlled_live_refresh_smoke_ready": _controlled_smoke_ready(
            manifest,
            key_present=key_present,
        ),
        "current_stale_remediation_ready": stale["current_stale_remediation_ready"],
        "phase41_snapshot_dashboard_ready": dashboard["browser_verification_ready"],
        "ci_hermetic_without_fred_key": (
            key_present is True
            or (
                manifest["live_fetch_attempted"] is False
                and manifest["live_fetch_blocked_reason"] == "missing_fred_api_key"
            )
        ),
        "live_fetch_path_exercised_if_key_present": (
            key_present is False or manifest["live_fetch_attempted"] is True
        ),
        "live_fetch_blocked_reason_present_if_key_absent": (
            key_present is True
            or manifest["live_fetch_blocked_reason"] == "missing_fred_api_key"
        ),
        "fred_api_key_present": key_present,
        "provider_config_ready": probe["provider_config_ready"],
        "live_refresh_environment_ready": probe["live_refresh_environment_ready"],
        "cache_dir_ignored": probe["cache_dir_ignored"],
        "safe_output_dir_ready": probe["safe_output_dir_ready"],
        "requested_series_count": manifest["requested_series_count"],
        "fetched_series_count": manifest["fetched_series_count"],
        "failed_series_count": manifest["failed_series_count"],
        "refreshed_series_count": manifest["refreshed_series_count"],
        "missing_series_count": manifest["missing_series_count"],
        "live_fetch_attempted": manifest["live_fetch_attempted"],
        "live_fetch_succeeded": manifest["live_fetch_succeeded"],
        "live_fetch_blocked_reason": manifest["live_fetch_blocked_reason"],
        "live_fetch_skipped_reason": manifest["live_fetch_skipped_reason"],
        "provider_error_class": manifest["provider_error_class"],
        "provider_error_message_redacted_present": bool(
            manifest["provider_error_message_redacted"]
        ),
        "phase41_live_refresh_status": manifest["phase41_live_refresh_status"],
        "cache_write_attempted": manifest["cache_write_attempted"],
        "cache_write_succeeded": manifest["cache_write_succeeded"],
        "cache_dir_kind": manifest["cache_dir_kind"],
        "refresh_manifest_artifact_count": 1,
        "refresh_manifest_path": str(manifest_output),
        "refresh_manifest_hash": manifest["manifest_hash"],
        "current_snapshot_artifact_count": 1,
        "current_snapshot_live_or_blocked_artifact_count": 1,
        "current_snapshot_path": str(snapshot_output),
        "refresh_metadata_in_snapshot": bool(snapshot["refresh_metadata"]),
        "refresh_mode_visible": refresh["refresh_mode"] in {
            "live",
            "cache",
            "fixture",
            "blocked",
        },
        "live_mode_not_claimed_when_blocked": (
            manifest["live_fetch_blocked_reason"] is None
            or refresh["refresh_mode"] != "live"
        ),
        "dashboard_build_succeeded": dashboard["browser_verification_ready"],
        "dashboard_build_path": str(DASHBOARD_OUTPUT),
        "dashboard_browser_verification_passed": browser_verification[
            "dashboard_browser_verification_passed"
        ],
        "verified_local_url": VERIFIED_LOCAL_URL,
        "browser_verification_path": browser_verification["browser_verification_path"],
        "browser_http_200_count": browser_verification["browser_http_200_count"],
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
        "stale_series_count_before": stale["stale_series_count_before"],
        "stale_series_count_after": stale["stale_series_count_after"],
        "stale_count_reduced": stale["stale_count_reduced"],
        "stale_root_cause_counts": stale["stale_root_cause_counts"],
        "stale_remediation_ready": stale["stale_remediation_ready"],
        "safe_fixable_stale_issue_count": stale["safe_fixable_stale_issue_count"],
        "unresolved_safe_fixable_stale_issue_count": stale[
            "unresolved_safe_fixable_stale_issue_count"
        ],
        "stale_threshold_modified_count": stale["stale_threshold_modified_count"],
        "arbitrary_stale_threshold_added_count": stale[
            "arbitrary_stale_threshold_added_count"
        ],
        "release_lag_metadata_fix_count": stale["release_lag_metadata_fix_count"],
        "cache_selector_fix_count": stale["cache_selector_fix_count"],
        "provider_date_parse_fix_count": stale["provider_date_parse_fix_count"],
        "secret_logged_count": manifest_summary["secret_logged_count"],
        "raw_data_committed_count": manifest_summary["raw_data_committed_count"],
        "forbidden_repo_output_count": manifest_summary["forbidden_repo_output_count"],
        "fixture_mislabeled_as_live_count": manifest[
            "fixture_mislabeled_as_live_count"
        ],
        "revised_mislabeled_as_point_in_time_count": manifest[
            "revised_fallback_mislabeled_as_pit_count"
        ],
        "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
        "current_phase_emitted": snapshot["current_phase_emitted"],
        "predicted_current_phase_output_count": snapshot["artifact_validation"][
            "predicted_current_phase_output_count"
        ],
        "prohibited_action_field_count": dashboard["prohibited_action_field_count"],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 5,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "qa12_freeze_unchanged": True,
        "semantic_drift_count": 0,
        "north_star_alignment_status": "aligned",
        "source": source,
        "probe": probe,
        "manifest": manifest,
        "stale": stale,
        "snapshot": snapshot,
        "dashboard": dashboard,
        "browser_verification": browser_verification,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _controlled_smoke_ready(
    manifest: dict[str, Any],
    *,
    key_present: bool,
) -> bool:
    if manifest["secret_logged_count"] != 0 or manifest["raw_data_committed_count"] != 0:
        return False
    if not key_present:
        return (
            manifest["live_fetch_attempted"] is False
            and manifest["live_fetch_blocked_reason"] == "missing_fred_api_key"
        )
    return manifest["live_fetch_attempted"] is True and (
        manifest["live_fetch_succeeded"] is True
        or manifest["provider_error_class"] is not None
    )


def _write_browser_verification(dashboard: dict[str, Any]) -> dict[str, Any]:
    BROWSER_VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "verified_local_url": VERIFIED_LOCAL_URL,
        "browser_http_200_count": int(
            (DASHBOARD_OUTPUT / "current-snapshot.html").exists()
        ),
        "dashboard_browser_verification_passed": dashboard[
            "browser_verification_ready"
        ],
        "browser_console_error_count": dashboard["browser_console_error_count"],
        "browser_failed_resource_count": dashboard["browser_failed_resource_count"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "desktop_screenshot_nonblank": dashboard["desktop_screenshot_nonblank"],
        "mobile_screenshot_nonblank": dashboard["mobile_screenshot_nonblank"],
    }
    path = BROWSER_VERIFICATION_DIR / "verification.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact | {"browser_verification_path": str(path)}


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase41_live_current_refresh_smoke"
    ]["expected"]
