"""Temporal integrity helpers for point-in-time audit fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


class TemporalIntegrityError(ValueError):
    """Raised when temporal integrity metadata is missing or invalid."""


@dataclass(frozen=True)
class TemporalFilterResult:
    """Point-in-time filter result for synthetic audit records."""

    included_records: list[dict[str, Any]]
    excluded_records: list[dict[str, Any]]
    blocked_records: list[dict[str, Any]]


def filter_point_in_time_records(
    records: list[dict[str, Any]],
    as_of: str | date,
) -> TemporalFilterResult:
    """Apply the minimum QA0 point-in-time filter to synthetic records."""

    as_of_date = _parse_date(as_of, "as_of")
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    required = ("observation_date", "available_at", "vintage_date")

    for record in records:
        missing = [field for field in required if field not in record]
        if missing:
            blocked.append(
                {
                    **record,
                    "blocked_reason": "missing_availability_metadata",
                    "missing_fields": missing,
                }
            )
            continue
        observation_date = _parse_date(record["observation_date"], "observation_date")
        available_at = _parse_date(record["available_at"], "available_at")
        vintage_date = _parse_date(record["vintage_date"], "vintage_date")
        if (
            observation_date <= as_of_date
            and available_at <= as_of_date
            and vintage_date <= as_of_date
        ):
            included.append(record)
        else:
            reason = "post_release" if available_at > as_of_date else "post_as_of_revision"
            excluded.append({**record, "excluded_reason": reason})

    return TemporalFilterResult(
        included_records=included,
        excluded_records=excluded,
        blocked_records=blocked,
    )


def summarize_temporal_integrity(
    lag_registry_path: str | Path = "specs/common/series_release_lag_registry.yaml",
) -> dict[str, Any]:
    """Summarize current release/vintage readiness from the lag registry."""

    registry = _load_root(lag_registry_path, "series_release_lag_registry")
    series = registry.get("series", [])
    if not isinstance(series, list):
        raise TemporalIntegrityError("series_release_lag_registry.series must be a list")
    series_with_lag = [
        item
        for item in series
        if isinstance(item, dict) and item.get("default_release_lag_days") is not None
    ]
    series_with_vintage = [
        item for item in series if isinstance(item, dict) and item.get("vintage_support") is True
    ]
    missing_availability = [
        item
        for item in series
        if not isinstance(item, dict)
        or item.get("default_release_lag_days") is None
        or item.get("vintage_support") is not True
    ]
    summary = registry.get("summary", {})
    blocker_count = len(missing_availability)
    return {
        "audited_series_count": len(series),
        "series_with_release_lag_count": len(series_with_lag),
        "series_with_vintage_support_count": len(series_with_vintage),
        "series_missing_availability_metadata_count": len(missing_availability),
        "revised_data_only": bool(summary.get("revised_data_only", True)),
        "vintage_data_supported": bool(summary.get("vintage_data_supported", False)),
        "point_in_time_backtest_ready": bool(
            summary.get("point_in_time_backtest_ready", False)
        ),
        "temporal_leakage_blocker_count": blocker_count,
    }


def _load_root(path: str | Path, root_key: str) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get(root_key), dict):
        raise TemporalIntegrityError(f"{path} must contain root mapping {root_key}")
    return {str(key): value for key, value in payload[root_key].items()}


def _parse_date(value: str | date, field: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise TemporalIntegrityError(f"{field} must be ISO date: {value}") from exc
