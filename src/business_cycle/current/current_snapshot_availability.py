"""Current-as-of research snapshot source availability metadata."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)


DEFAULT_SERIES_REGISTRY_PATH = Path("specs/common/series_release_lag_registry.yaml")
DATA_MODE = "revised_metadata_fixture"


def build_current_snapshot_availability(
    *,
    snapshot_as_of: str | None = None,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
    data_cache_dir: str | Path | None = None,
    allow_fixture_fallback: bool = False,
    no_live_fetch: bool = True,
) -> dict[str, Any]:
    if refresh_manifest_path is not None:
        refresh_manifest = json.loads(Path(refresh_manifest_path).read_text(encoding="utf-8"))
    if refresh_manifest is not None:
        return _availability_from_refresh_manifest(refresh_manifest)
    if data_cache_dir is not None or allow_fixture_fallback:
        refresh_manifest = build_current_data_refresh_manifest(
            snapshot_as_of=snapshot_as_of,
            no_live_fetch=no_live_fetch,
            allow_fixture_fallback=allow_fixture_fallback,
            cache_dir=data_cache_dir,
            registry_path=registry_path,
        )
        return _availability_from_refresh_manifest(refresh_manifest)
    snapshot_as_of = snapshot_as_of or datetime.now(timezone.utc).date().isoformat()
    rows = _load_series_rows(registry_path)
    requested = [_availability_row(row, snapshot_as_of=snapshot_as_of) for row in rows]
    available = [row for row in requested if row["availability_status"] == "available"]
    missing = [row for row in requested if row["availability_status"] == "missing"]
    stale = [row for row in requested if row["stale"]]
    unavailable = [
        row for row in requested if row["availability_status"] == "unavailable"
    ]
    latest_by_series = {
        row["series_id"]: row["latest_observation_date"] for row in requested
    }
    release_lag_complete = [
        row for row in requested if row["release_lag_metadata_complete"]
    ]
    release_lag_missing = [
        row for row in requested if not row["release_lag_metadata_complete"]
    ]
    return {
        "phase": "39",
        "snapshot_as_of": snapshot_as_of,
        "data_mode": DATA_MODE,
        "requested_data_sources": requested,
        "requested_series_count": len(requested),
        "available_series_count": len(available),
        "missing_series_count": len(missing),
        "stale_series_count": len(stale),
        "unavailable_series_count": len(unavailable),
        "latest_observation_date_by_series": latest_by_series,
        "release_lag_metadata_complete_count": len(release_lag_complete),
        "release_lag_metadata_missing_count": len(release_lag_missing),
        "live_fetch_attempted": False,
        "live_fetch_succeeded": False,
        "live_fetch_failed_reason": "live_fetch_disabled_for_phase39_research_snapshot",
        "live_fetch_skipped_reason": "live_fetch_disabled_for_phase39_research_snapshot",
        "provider_error_class": None,
        "refresh_mode": "fixture",
        "stale_series_count_before": len(stale),
        "stale_series_count_after": len(stale),
        "refreshed_series_count": 0,
        "source_mode_by_series": {
            row["series_id"]: "fixture" for row in requested
        },
        "refresh_manifest_artifact_count": 0,
        "cache_used": False,
        "fixture_used": True,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "forbidden_repo_output_count": 0,
    }


def summarize_current_snapshot_availability() -> dict[str, Any]:
    availability = build_current_snapshot_availability()
    return {
        key: availability[key]
        for key in (
            "phase",
            "snapshot_as_of",
            "data_mode",
            "requested_series_count",
            "available_series_count",
            "missing_series_count",
            "stale_series_count",
            "unavailable_series_count",
            "release_lag_metadata_complete_count",
            "release_lag_metadata_missing_count",
            "live_fetch_attempted",
            "live_fetch_succeeded",
            "live_fetch_failed_reason",
            "live_fetch_skipped_reason",
            "provider_error_class",
            "refresh_mode",
            "stale_series_count_before",
            "stale_series_count_after",
            "refreshed_series_count",
            "cache_used",
            "fixture_used",
            "secret_logged_count",
            "raw_data_committed_count",
            "forbidden_repo_output_count",
        )
    } | {"current_snapshot_availability_ready": _availability_ready(availability)}


def _availability_from_refresh_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    rows = [_availability_row_from_refresh(row) for row in manifest["series_refresh_rows"]]
    available = [row for row in rows if row["availability_status"] == "available"]
    missing = [row for row in rows if row["availability_status"] == "missing"]
    stale = [row for row in rows if row["stale"]]
    unavailable = [row for row in rows if row["availability_status"] == "unavailable"]
    latest_by_series = {
        row["series_id"]: row["latest_observation_date"] for row in rows
    }
    release_lag_complete = [
        row for row in rows if row["release_lag_metadata_complete"]
    ]
    release_lag_missing = [
        row for row in rows if not row["release_lag_metadata_complete"]
    ]
    return {
        "phase": "40",
        "snapshot_as_of": manifest["snapshot_as_of"],
        "data_mode": manifest["data_mode"],
        "requested_data_sources": rows,
        "requested_series_count": manifest["requested_series_count"],
        "available_series_count": len(available),
        "missing_series_count": len(missing),
        "stale_series_count": len(stale),
        "unavailable_series_count": len(unavailable),
        "latest_observation_date_by_series": latest_by_series,
        "release_lag_metadata_complete_count": len(release_lag_complete),
        "release_lag_metadata_missing_count": len(release_lag_missing),
        "live_fetch_attempted": manifest["live_fetch_attempted"],
        "live_fetch_succeeded": manifest["live_fetch_succeeded"],
        "live_fetch_failed_reason": (
            manifest["provider_error_class"]
            or manifest["live_fetch_skipped_reason"]
            or "none"
        ),
        "live_fetch_skipped_reason": manifest["live_fetch_skipped_reason"],
        "provider_error_class": manifest["provider_error_class"],
        "refresh_mode": _refresh_mode(manifest),
        "stale_series_count_before": manifest["stale_series_count_before"],
        "stale_series_count_after": manifest["stale_series_count_after"],
        "refreshed_series_count": manifest["refreshed_series_count"],
        "source_mode_by_series": manifest["source_mode_by_series"],
        "refresh_manifest_artifact_count": 1,
        "refresh_manifest_hash": manifest["manifest_hash"],
        "cache_used": manifest["cache_used"],
        "fixture_used": manifest["fixture_used"],
        "secret_logged_count": manifest["secret_logged_count"],
        "raw_data_committed_count": manifest["raw_data_committed_count"],
        "forbidden_repo_output_count": manifest["forbidden_repo_output_count"],
        "refresh_manifest": manifest,
    }


def _availability_row_from_refresh(row: dict[str, Any]) -> dict[str, Any]:
    if row["source_mode"] in {"unsupported", "unsupported_fixture", "provider_error"}:
        status = "missing"
    elif row["source_mode"] in {"derived_not_fetched"}:
        status = "available"
    elif row["point_in_time_eligible"] is False:
        status = "unavailable"
    else:
        status = "available"
    return {
        "series_id": row["series_id"],
        "source": row["source"],
        "frequency": row["frequency"],
        "release_family": row["release_family"],
        "availability_status": status,
        "point_in_time_eligible": row["point_in_time_eligible"],
        "release_lag_metadata_complete": row["release_lag_metadata_complete"],
        "latest_observation_date": row["latest_observation_date"],
        "latest_verified_vintage_date": row["latest_verified_vintage_date"],
        "source_mode": row["source_mode"],
        "stale": row["stale_after_refresh"],
        "stale_reason": (
            "latest observation precedes snapshot_as_of"
            if row["stale_after_refresh"]
            else "not stale"
        ),
        "missing_reason": (
            "refresh source missing or unsupported"
            if status == "missing"
            else None
        ),
        "unavailable_reason": (
            "series is not point-in-time eligible" if status == "unavailable" else None
        ),
    }


def _refresh_mode(manifest: dict[str, Any]) -> str:
    if manifest["live_fetch_succeeded"]:
        return "live"
    if manifest["cache_used"]:
        return "cache"
    return "fixture"


def _availability_ready(availability: dict[str, Any]) -> bool:
    return (
        availability["requested_series_count"] > 0
        and availability["snapshot_as_of"] != ""
        and availability["release_lag_metadata_complete_count"] > 0
        and availability["live_fetch_attempted"] is False
        and availability["secret_logged_count"] == 0
        and availability["raw_data_committed_count"] == 0
        and availability["forbidden_repo_output_count"] == 0
    )


def _load_series_rows(path: str | Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = payload["series_release_lag_registry"]["series"]
    return sorted(rows, key=lambda row: str(row["series_id"]))


def _availability_row(row: dict[str, Any], *, snapshot_as_of: str) -> dict[str, Any]:
    latest = str(row.get("latest_verified_vintage_date") or "not_verified_in_repo")
    release_lag = row.get("release_lag_rule")
    metadata_complete = bool(release_lag) and release_lag != "unsupported"
    point_in_time_eligible = bool(row.get("point_in_time_eligible"))
    if not metadata_complete:
        status = "missing"
    elif not point_in_time_eligible:
        status = "unavailable"
    else:
        status = "available"
    stale = latest in {"unknown", "not_verified_in_repo"} or latest < snapshot_as_of
    latest_observation = (
        latest
        if latest not in {"unknown", "not_verified_in_repo"}
        else str(row.get("scenario_coverage_end", "not_verified_in_repo"))
    )
    return {
        "series_id": str(row["series_id"]),
        "source": str(row.get("source", "unknown")),
        "frequency": str(row.get("frequency", "unknown")),
        "release_family": str(row.get("release_family", "unknown")),
        "availability_status": status,
        "point_in_time_eligible": point_in_time_eligible,
        "release_lag_metadata_complete": metadata_complete,
        "latest_observation_date": latest_observation,
        "latest_verified_vintage_date": latest,
        "stale": stale,
        "stale_reason": (
            "latest verified vintage precedes snapshot_as_of"
            if stale
            else "not stale"
        ),
        "missing_reason": (
            "release lag metadata missing or unsupported"
            if status == "missing"
            else None
        ),
        "unavailable_reason": (
            "series is not point-in-time eligible"
            if status == "unavailable"
            else None
        ),
    }
