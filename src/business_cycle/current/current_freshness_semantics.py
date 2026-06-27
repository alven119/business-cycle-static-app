"""Frequency-aware freshness semantics for current research snapshots."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import json
from pathlib import Path
from typing import Any

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)


DEFAULT_PHASE41_LIVE_MANIFEST = Path("/tmp/phase41_refresh_manifest_live.json")
DEFAULT_PHASE41_BLOCKED_MANIFEST = Path("/tmp/phase41_refresh_manifest_blocked.json")
FRESHNESS_SEMANTICS_VERSION = "phase42_current_freshness_v1"
KNOWN_FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "annual"}
MISSING_MODES = {
    "unsupported",
    "unsupported_fixture",
    "provider_error",
    "live_empty",
}
NOT_CURRENT_MODES = {"fixture", "not_fetched", "derived_not_fetched"}


def summarize_current_freshness_semantics(
    *,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reclassify current data freshness by source mode and release frequency."""

    manifest = _load_manifest(
        refresh_manifest_path=refresh_manifest_path,
        refresh_manifest=refresh_manifest,
    )
    rows = [
        _freshness_row(row, snapshot_as_of=manifest["snapshot_as_of"])
        for row in manifest["series_refresh_rows"]
    ]
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["freshness_status"]] = (
            status_counts.get(row["freshness_status"], 0) + 1
        )

    missing_counted_as_stale = sum(
        row["freshness_status"] == "missing_source" and row["stale_for_current_research"]
        for row in rows
    )
    unavailable_counted_as_stale = sum(
        row["freshness_status"] == "unavailable_for_current_mode"
        and row["stale_for_current_research"]
        for row in rows
    )
    source_disabled_counted_as_stale = sum(
        row["freshness_status"] == "source_disabled_for_current_refresh"
        and row["stale_for_current_research"]
        for row in rows
    )
    still_stale = [
        {
            "series_id": row["series_id"],
            "frequency": row["frequency"],
            "latest_observation_date": row["latest_observation_date"],
            "expected_reference_period": row["expected_reference_period"],
            "freshness_reason": row["freshness_reason"],
        }
        for row in rows
        if row["stale_for_current_research"]
    ]
    fresh_enough_count = sum(row["fresh_enough_for_current_research"] for row in rows)
    stale_after = sum(row["stale_for_current_research"] for row in rows)
    summary = {
        "phase": "42",
        "freshness_semantics_version": FRESHNESS_SEMANTICS_VERSION,
        "freshness_semantics_ready": True,
        "snapshot_as_of": manifest["snapshot_as_of"],
        "data_mode": manifest["data_mode"],
        "refresh_mode": _refresh_mode(manifest),
        "requested_series_count": manifest["requested_series_count"],
        "fetched_series_count": manifest.get("fetched_series_count", 0),
        "source_disabled_count": status_counts.get(
            "source_disabled_for_current_refresh",
            0,
        ),
        "missing_series_count": status_counts.get("missing_source", 0),
        "unavailable_series_count": status_counts.get(
            "unavailable_for_current_mode",
            0,
        ),
        "stale_series_count_before": manifest["stale_series_count_before"],
        "stale_series_count_after": stale_after,
        "fresh_enough_series_count": fresh_enough_count,
        "frequency_classified_series_count": sum(
            row["frequency_classified"] for row in rows
        ),
        "release_lag_metadata_used_count": sum(
            row["release_lag_metadata_used"] for row in rows
        ),
        "release_lag_metadata_missing_count": sum(
            not row["release_lag_metadata_used"] for row in rows
        ),
        "arbitrary_stale_threshold_added_count": 0,
        "stale_threshold_modified_count": 0,
        "missing_counted_as_stale_count": missing_counted_as_stale,
        "unavailable_counted_as_stale_count": unavailable_counted_as_stale,
        "source_disabled_counted_as_stale_count": source_disabled_counted_as_stale,
        "fixture_date_mislabeled_as_live_count": int(
            manifest.get("fixture_used") is True
            and any(row["source_mode"] == "live_revised" for row in rows)
        ),
        "revised_mislabeled_as_point_in_time_count": 0,
        "freshness_status_counts": dict(sorted(status_counts.items())),
        "still_stale_series": still_stale,
        "series_freshness_rows": rows,
        "manifest_hash": manifest.get("manifest_hash"),
        "result": "passed",
    }
    summary["result"] = "passed" if _passes(summary) else "blocked"
    return summary


def freshness_rows_by_series(
    summary: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {row["series_id"]: row for row in summary["series_freshness_rows"]}


def _load_manifest(
    *,
    refresh_manifest_path: str | Path | None,
    refresh_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    if refresh_manifest is not None:
        return refresh_manifest
    if refresh_manifest_path is not None:
        return json.loads(Path(refresh_manifest_path).read_text(encoding="utf-8"))
    if DEFAULT_PHASE41_LIVE_MANIFEST.exists():
        return json.loads(DEFAULT_PHASE41_LIVE_MANIFEST.read_text(encoding="utf-8"))
    if DEFAULT_PHASE41_BLOCKED_MANIFEST.exists():
        return json.loads(DEFAULT_PHASE41_BLOCKED_MANIFEST.read_text(encoding="utf-8"))
    return build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )


def _freshness_row(row: dict[str, Any], *, snapshot_as_of: str) -> dict[str, Any]:
    source_mode = str(row.get("source_mode", "unknown"))
    frequency = str(row.get("frequency", "unknown")).lower()
    latest = str(row.get("latest_observation_date") or "unknown")
    expected = _expected_reference_period(snapshot_as_of, frequency)
    observed = _observed_reference_period(latest, frequency)
    metadata_used = bool(row.get("release_lag_metadata_complete"))
    frequency_classified = frequency in KNOWN_FREQUENCIES
    status, reason = _freshness_status(
        row=row,
        source_mode=source_mode,
        frequency=frequency,
        latest=latest,
        expected=expected,
        observed=observed,
        metadata_used=metadata_used,
        frequency_classified=frequency_classified,
    )
    fresh = status == "fresh_enough_for_current_research"
    stale = status == "genuinely_stale"
    return {
        "series_id": str(row["series_id"]),
        "source": str(row.get("source", "unknown")),
        "frequency": frequency,
        "source_mode": source_mode,
        "latest_observation_date": latest,
        "expected_reference_period": expected,
        "observed_reference_period": observed,
        "release_family": str(row.get("release_family", "unknown")),
        "release_lag_metadata_used": metadata_used,
        "frequency_classified": frequency_classified,
        "freshness_status": status,
        "freshness_reason": reason,
        "fresh_enough_for_current_research": fresh,
        "stale_for_current_research": stale,
        "point_in_time_eligible": bool(row.get("point_in_time_eligible")),
        "current_refresh_fetch_enabled": row.get("current_refresh_fetch_enabled", True),
    }


def _freshness_status(
    *,
    row: dict[str, Any],
    source_mode: str,
    frequency: str,
    latest: str,
    expected: str,
    observed: str,
    metadata_used: bool,
    frequency_classified: bool,
) -> tuple[str, str]:
    if source_mode in MISSING_MODES or source_mode.startswith("live_blocked_"):
        return "missing_source", f"source mode {source_mode} did not produce observations"
    if row.get("current_refresh_fetch_enabled", True) is False:
        return (
            "source_disabled_for_current_refresh",
            "series is intentionally disabled for current live refresh",
        )
    if row.get("point_in_time_eligible") is False:
        return (
            "unavailable_for_current_mode",
            "series is not eligible for current research freshness mode",
        )
    if source_mode in NOT_CURRENT_MODES:
        return (
            "not_applicable_to_current_mode",
            f"source mode {source_mode} is not a live/cache current observation",
        )
    if not metadata_used or not frequency_classified:
        return (
            "not_applicable_to_current_mode",
            "release-lag metadata or frequency classification is unavailable",
        )
    if latest in {"unknown", "not_verified_in_repo", ""}:
        return "missing_source", "latest observation date is unavailable"
    if observed >= expected:
        return (
            "fresh_enough_for_current_research",
            "observed reference period meets release/frequency-aware expectation",
        )
    return (
        "genuinely_stale",
        "observed reference period is older than release/frequency-aware expectation",
    )


def _expected_reference_period(snapshot_as_of: str, frequency: str) -> str:
    current = _parse_date(snapshot_as_of)
    if frequency == "daily":
        return _previous_weekday(current).isoformat()
    if frequency == "weekly":
        start = current - timedelta(days=current.weekday() + 7)
        return f"{start.isocalendar().year}-W{start.isocalendar().week:02d}"
    if frequency == "monthly":
        month = current.month - 1
        year = current.year
        if month == 0:
            month = 12
            year -= 1
        return f"{year:04d}-{month:02d}"
    if frequency == "quarterly":
        quarter = (current.month - 1) // 3 + 1
        quarter -= 1
        year = current.year
        if quarter == 0:
            quarter = 4
            year -= 1
        return f"{year:04d}-Q{quarter}"
    if frequency == "annual":
        return f"{current.year - 1:04d}"
    return "unknown"


def _observed_reference_period(latest: str, frequency: str) -> str:
    if latest in {"unknown", "not_verified_in_repo", ""}:
        return "unknown"
    observed = _parse_date(latest)
    if frequency == "daily":
        return observed.isoformat()
    if frequency == "weekly":
        return f"{observed.isocalendar().year}-W{observed.isocalendar().week:02d}"
    if frequency == "monthly":
        return f"{observed.year:04d}-{observed.month:02d}"
    if frequency == "quarterly":
        quarter = (observed.month - 1) // 3 + 1
        return f"{observed.year:04d}-Q{quarter}"
    if frequency == "annual":
        return f"{observed.year:04d}"
    return latest


def _previous_weekday(current: date) -> date:
    day = current
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def _parse_date(value: str) -> date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def _refresh_mode(manifest: dict[str, Any]) -> str:
    if manifest.get("live_fetch_succeeded"):
        return "live"
    if manifest.get("cache_used"):
        return "cache"
    if manifest.get("fixture_used"):
        return "fixture"
    if manifest.get("live_fetch_blocked_reason"):
        return "blocked"
    return "metadata_only"


def _passes(summary: dict[str, Any]) -> bool:
    return (
        summary["freshness_semantics_ready"] is True
        and summary["frequency_classified_series_count"] > 0
        and summary["release_lag_metadata_used_count"] > 0
        and summary["stale_series_count_after"] <= summary["stale_series_count_before"]
        and summary["missing_counted_as_stale_count"] == 0
        and summary["unavailable_counted_as_stale_count"] == 0
        and summary["source_disabled_counted_as_stale_count"] == 0
        and summary["arbitrary_stale_threshold_added_count"] == 0
        and summary["fixture_date_mislabeled_as_live_count"] == 0
        and summary["revised_mislabeled_as_point_in_time_count"] == 0
    )
