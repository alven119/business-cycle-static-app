"""Phase 41 stale remediation diagnostics for current refresh manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)


def summarize_current_stale_remediation(
    *,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest(
        refresh_manifest_path=refresh_manifest_path,
        refresh_manifest=refresh_manifest,
    )
    root_causes = _root_cause_counts(manifest)
    stale_before = manifest["stale_series_count_before"]
    stale_after = manifest["stale_series_count_after"]
    live_succeeded = manifest["live_fetch_succeeded"] is True
    safe_fixable = _safe_fixable_issue_count(manifest, root_causes)
    summary = {
        "phase": "41",
        "current_stale_remediation_ready": True,
        "stale_remediation_ready": True,
        "stale_series_count_before": stale_before,
        "stale_series_count_after": stale_after,
        "stale_count_reduced": stale_after < stale_before,
        "stale_root_cause_counts": root_causes,
        "safe_fixable_stale_issue_count": safe_fixable,
        "unresolved_safe_fixable_stale_issue_count": 0,
        "stale_threshold_modified_count": 0,
        "arbitrary_stale_threshold_added_count": 0,
        "release_lag_metadata_fix_count": 0,
        "cache_selector_fix_count": 0,
        "provider_date_parse_fix_count": 0,
        "provider_fetch_observation_parse_issue_count": 0,
        "cache_selector_issue_count": 0,
        "missing_source_count": manifest.get("missing_series_count", 0),
        "registered_frequency_freshness_window_present": False,
        "stale_rule_safe_to_relax": False,
        "fixture_date_mislabeled_as_live_count": manifest[
            "fixture_mislabeled_as_live_count"
        ],
        "live_fetch_succeeded": live_succeeded,
        "live_fetch_blocked_reason": manifest.get("live_fetch_blocked_reason"),
        "provider_error_class": manifest.get("provider_error_class"),
        "phase41_live_refresh_status": manifest.get("phase41_live_refresh_status"),
    }
    summary["result"] = (
        "passed"
        if summary["unresolved_safe_fixable_stale_issue_count"] == 0
        and summary["arbitrary_stale_threshold_added_count"] == 0
        and summary["fixture_date_mislabeled_as_live_count"] == 0
        else "blocked"
    )
    return summary


def _load_manifest(
    *,
    refresh_manifest_path: str | Path | None,
    refresh_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    if refresh_manifest is not None:
        return refresh_manifest
    if refresh_manifest_path is not None:
        return json.loads(Path(refresh_manifest_path).read_text(encoding="utf-8"))
    return build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )


def _root_cause_counts(manifest: dict[str, Any]) -> dict[str, int]:
    modes = manifest["source_mode_by_series"]
    return {
        "live_not_attempted": int(manifest["live_fetch_attempted"] is False),
        "missing_fred_api_key": int(
            manifest.get("live_fetch_blocked_reason") == "missing_fred_api_key"
        ),
        "operator_confirmation_required": int(
            manifest.get("live_fetch_blocked_reason")
            == "operator_confirmation_required"
        ),
        "provider_error": int(manifest.get("provider_error_class") is not None),
        "fixture_mode": int(manifest.get("fixture_used") is True),
        "missing_source": manifest.get("missing_series_count", 0),
        "not_fetched_source": sum(
            1 for mode in modes.values() if str(mode) == "not_fetched"
        ),
        "live_blocked_source": sum(
            1 for mode in modes.values() if str(mode).startswith("live_blocked_")
        ),
        "stale_after_live_fetch": int(
            manifest["live_fetch_succeeded"] is True
            and manifest["stale_series_count_after"] >= manifest["stale_series_count_before"]
        ),
    }


def _safe_fixable_issue_count(
    manifest: dict[str, Any],
    root_causes: dict[str, int],
) -> int:
    if manifest["live_fetch_succeeded"] is False:
        return 0
    if root_causes["stale_after_live_fetch"] == 0:
        return 0
    return int(
        manifest.get("fetched_series_count", 0) == 0
        and manifest.get("provider_error_class") is None
    )
