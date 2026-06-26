"""Current-as-of research snapshot source availability metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SERIES_REGISTRY_PATH = Path("specs/common/series_release_lag_registry.yaml")
DATA_MODE = "revised_metadata_fixture"


@lru_cache(maxsize=1)
def build_current_snapshot_availability(
    *,
    snapshot_as_of: str | None = None,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
) -> dict[str, Any]:
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
            "cache_used",
            "fixture_used",
            "secret_logged_count",
            "raw_data_committed_count",
            "forbidden_repo_output_count",
        )
    } | {"current_snapshot_availability_ready": _availability_ready(availability)}


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
