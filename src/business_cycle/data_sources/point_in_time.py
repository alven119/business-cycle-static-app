"""Point-in-time observation selection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable

import pandas as pd


class PointInTimeError(ValueError):
    """Raised when strict point-in-time selection cannot be performed."""


@dataclass(frozen=True)
class PointInTimeObservation:
    """One observation with real-time availability metadata."""

    series_id: str
    observation_date: date
    value: float
    realtime_start: date
    realtime_end: date | None
    source: str
    data_mode: str
    availability_precision: str
    fetched_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PointInTimeSnapshot:
    """A selected as-of view for one series."""

    series_id: str
    as_of: date
    observations: tuple[PointInTimeObservation, ...]
    selection_mode: str
    point_in_time: bool
    warnings: tuple[str, ...] = ()
    missing_series: tuple[str, ...] = ()
    proxy_series: tuple[str, ...] = ()


def select_vintage_as_of(
    rows: Iterable[dict[str, Any]] | pd.DataFrame,
    *,
    series_id: str,
    as_of: str | date,
    source: str = "alfred",
    availability_precision: str = "day",
) -> PointInTimeSnapshot:
    """Select observations whose real-time interval was active at end-of-day ``as_of``."""

    as_of_date = _parse_date(as_of, "as_of")
    normalized = _normalize_rows(rows, require_realtime=True)
    eligible: list[dict[str, Any]] = []
    for row in normalized:
        if _parse_numeric_value(row["value"]) is None:
            continue
        observation_date = _parse_date(row["observation_date"], "observation_date")
        realtime_start = _parse_date(row["realtime_start"], "realtime_start")
        realtime_end = _parse_open_end(row.get("realtime_end"))
        if observation_date > as_of_date or realtime_start > as_of_date:
            continue
        if realtime_end is not None and as_of_date > realtime_end:
            continue
        eligible.append(row)

    by_observation: dict[date, dict[str, Any]] = {}
    for row in eligible:
        observation_date = _parse_date(row["observation_date"], "observation_date")
        current = by_observation.get(observation_date)
        if current is None or _parse_date(row["realtime_start"], "realtime_start") > _parse_date(
            current["realtime_start"], "realtime_start"
        ):
            by_observation[observation_date] = row

    observations = tuple(
        _make_observation(
            series_id=series_id,
            row=row,
            source=source,
            data_mode="vintage_as_of",
            availability_precision=availability_precision,
        )
        for _, row in sorted(by_observation.items(), key=lambda item: item[0])
    )
    snapshot = PointInTimeSnapshot(
        series_id=series_id,
        as_of=as_of_date,
        observations=observations,
        selection_mode="vintage_as_of",
        point_in_time=True,
    )
    validate_point_in_time_snapshot(snapshot)
    return snapshot


def select_initial_release_only(
    rows: Iterable[dict[str, Any]] | pd.DataFrame,
    *,
    series_id: str,
    as_of: str | date | None = None,
    source: str = "alfred",
    availability_precision: str = "day",
) -> PointInTimeSnapshot:
    """Select the first release for each observation date without claiming as-of-latest vintage."""

    as_of_date = _parse_date(as_of, "as_of") if as_of is not None else date.max
    normalized = _normalize_rows(rows, require_realtime=True)
    first_by_observation: dict[date, dict[str, Any]] = {}
    for row in normalized:
        if _parse_numeric_value(row["value"]) is None:
            continue
        observation_date = _parse_date(row["observation_date"], "observation_date")
        realtime_start = _parse_date(row["realtime_start"], "realtime_start")
        if observation_date > as_of_date or realtime_start > as_of_date:
            continue
        current = first_by_observation.get(observation_date)
        if current is None or realtime_start < _parse_date(
            current["realtime_start"], "realtime_start"
        ):
            first_by_observation[observation_date] = row

    observations = tuple(
        _make_observation(
            series_id=series_id,
            row=row,
            source=source,
            data_mode="initial_release_only",
            availability_precision=availability_precision,
        )
        for _, row in sorted(first_by_observation.items(), key=lambda item: item[0])
    )
    return PointInTimeSnapshot(
        series_id=series_id,
        as_of=as_of_date,
        observations=observations,
        selection_mode="initial_release_only",
        point_in_time=False,
        warnings=("initial_release_only_is_not_as_of_latest_vintage",),
    )


def select_release_lag_proxy(
    rows: Iterable[dict[str, Any]] | pd.DataFrame,
    *,
    series_id: str,
    as_of: str | date,
    release_lag_days: int,
    source: str = "revised",
) -> PointInTimeSnapshot:
    """Select revised observations delayed by a release-lag proxy."""

    as_of_date = _parse_date(as_of, "as_of")
    normalized = _normalize_rows(rows, require_realtime=False)
    observations: list[PointInTimeObservation] = []
    for row in normalized:
        value = _parse_numeric_value(row["value"])
        if value is None:
            continue
        observation_date = _parse_date(row["observation_date"], "observation_date")
        available_at = observation_date + timedelta(days=release_lag_days)
        if available_at > as_of_date:
            continue
        observations.append(
            PointInTimeObservation(
                series_id=series_id,
                observation_date=observation_date,
                value=value,
                realtime_start=available_at,
                realtime_end=None,
                source=source,
                data_mode="release_lag_adjusted_revised_proxy",
                availability_precision="day",
                fetched_at=_now_iso(),
                metadata={"release_lag_days": release_lag_days},
            )
        )
    return PointInTimeSnapshot(
        series_id=series_id,
        as_of=as_of_date,
        observations=tuple(observations),
        selection_mode="release_lag_adjusted_revised_proxy",
        point_in_time=False,
        warnings=("release_lag_proxy_is_not_point_in_time",),
        proxy_series=(series_id,),
    )


def validate_point_in_time_snapshot(snapshot: PointInTimeSnapshot) -> None:
    """Fail closed if strict point-in-time metadata is missing or inconsistent."""

    if snapshot.selection_mode != "vintage_as_of" or not snapshot.point_in_time:
        raise PointInTimeError("Strict point-in-time validation requires vintage_as_of mode")
    for observation in snapshot.observations:
        if observation.realtime_start > snapshot.as_of:
            raise PointInTimeError("Post-as-of revision leaked into snapshot")
        if observation.observation_date > snapshot.as_of:
            raise PointInTimeError("Not-yet-observed date leaked into snapshot")
        if observation.realtime_end is not None and snapshot.as_of > observation.realtime_end:
            raise PointInTimeError("Expired vintage leaked into snapshot")
        if observation.availability_precision != "day":
            raise PointInTimeError("Strict point-in-time snapshots require day precision")


def build_derived_snapshot(
    *,
    derived_series_id: str,
    input_snapshots: list[PointInTimeSnapshot],
    operation: str = "difference",
) -> PointInTimeSnapshot:
    """Build a strict derived snapshot from same-as-of input snapshots."""

    if not input_snapshots:
        raise PointInTimeError("Derived snapshot requires at least one input snapshot")
    as_of = input_snapshots[0].as_of
    missing = [snapshot.series_id for snapshot in input_snapshots if not snapshot.observations]
    non_strict = [
        snapshot.series_id
        for snapshot in input_snapshots
        if snapshot.selection_mode != "vintage_as_of" or not snapshot.point_in_time
    ]
    if any(snapshot.as_of != as_of for snapshot in input_snapshots):
        raise PointInTimeError("Derived snapshot inputs must use the same as_of date")
    if missing or non_strict:
        raise PointInTimeError(
            f"Derived strict snapshot blocked: missing={missing} non_strict={non_strict}"
        )
    if operation != "difference" or len(input_snapshots) != 2:
        raise PointInTimeError("Only two-input difference derived snapshots are supported")

    first = {obs.observation_date: obs for obs in input_snapshots[0].observations}
    second = {obs.observation_date: obs for obs in input_snapshots[1].observations}
    observations: list[PointInTimeObservation] = []
    for observation_date in sorted(first.keys() & second.keys()):
        left = first[observation_date]
        right = second[observation_date]
        available_at = max(left.realtime_start, right.realtime_start)
        observations.append(
            PointInTimeObservation(
                series_id=derived_series_id,
                observation_date=observation_date,
                value=left.value - right.value,
                realtime_start=available_at,
                realtime_end=None,
                source="derived",
                data_mode="vintage_as_of",
                availability_precision="day",
                fetched_at=max(left.fetched_at, right.fetched_at),
                metadata={
                    "input_series_ids": [left.series_id, right.series_id],
                    "availability_rule": "max_input_availability",
                    "vintage_rule": "all_inputs_same_as_of_snapshot",
                },
            )
        )
    snapshot = PointInTimeSnapshot(
        series_id=derived_series_id,
        as_of=as_of,
        observations=tuple(observations),
        selection_mode="vintage_as_of",
        point_in_time=True,
    )
    validate_point_in_time_snapshot(snapshot)
    return snapshot


def explain_snapshot_selection(snapshot: PointInTimeSnapshot) -> dict[str, Any]:
    """Return a compact explanation of snapshot selection semantics."""

    return {
        "series_id": snapshot.series_id,
        "as_of": snapshot.as_of.isoformat(),
        "selection_mode": snapshot.selection_mode,
        "point_in_time": snapshot.point_in_time,
        "observation_count": len(snapshot.observations),
        "warnings": list(snapshot.warnings),
        "missing_series": list(snapshot.missing_series),
        "proxy_series": list(snapshot.proxy_series),
    }


def snapshot_to_frame(snapshot: PointInTimeSnapshot) -> pd.DataFrame:
    """Convert a snapshot to the date/value frame expected by indicator scoring."""

    return pd.DataFrame(
        [
            {
                "series_id": observation.series_id,
                "date": observation.observation_date.isoformat(),
                "value": observation.value,
                "realtime_start": observation.realtime_start.isoformat(),
                "realtime_end": ""
                if observation.realtime_end is None
                else observation.realtime_end.isoformat(),
            }
            for observation in snapshot.observations
        ]
    )


def _normalize_rows(
    rows: Iterable[dict[str, Any]] | pd.DataFrame,
    *,
    require_realtime: bool,
) -> list[dict[str, Any]]:
    if isinstance(rows, pd.DataFrame):
        records = rows.to_dict(orient="records")
    else:
        records = [dict(row) for row in rows]
    normalized: list[dict[str, Any]] = []
    for row in records:
        if "observation_date" not in row and "date" in row:
            row["observation_date"] = row["date"]
        if "value" not in row:
            raise PointInTimeError("Rows must contain value")
        if require_realtime and (not row.get("realtime_start") or "realtime_end" not in row):
            raise PointInTimeError("Strict mode requires realtime_start and realtime_end metadata")
        normalized.append(row)
    return normalized


def _make_observation(
    *,
    series_id: str,
    row: dict[str, Any],
    source: str,
    data_mode: str,
    availability_precision: str,
) -> PointInTimeObservation:
    value = _parse_numeric_value(row["value"])
    if value is None:
        raise PointInTimeError("Observation value is missing")
    return PointInTimeObservation(
        series_id=str(row.get("series_id") or series_id),
        observation_date=_parse_date(row["observation_date"], "observation_date"),
        value=value,
        realtime_start=_parse_date(row["realtime_start"], "realtime_start"),
        realtime_end=_parse_open_end(row.get("realtime_end")),
        source=source,
        data_mode=data_mode,
        availability_precision=availability_precision,
        fetched_at=str(row.get("fetched_at") or _now_iso()),
        metadata=dict(row.get("metadata") or {}),
    )


def _parse_date(value: str | date, field: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise PointInTimeError(f"{field} must be ISO date: {value}") from exc


def _parse_open_end(value: Any) -> date | None:
    if value in (None, "", ".", "9999-12-31"):
        return None
    return _parse_date(value, "realtime_end")


def _parse_numeric_value(value: Any) -> float | None:
    if value in (None, "", "."):
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise PointInTimeError(f"Observation value must be numeric or missing: {value}") from exc


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
