"""Point-in-time derived indicator helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from business_cycle.data_sources.point_in_time import PointInTimeError, PointInTimeSnapshot


@dataclass(frozen=True)
class DerivedPointInTimeValue:
    series_id: str
    as_of: str
    selected_reference_month: str
    value: float
    formula_id: str
    formula_version: str
    input_snapshot_ids: tuple[str, ...]
    input_availability_dates: tuple[str, ...]
    availability_date: str
    temporal_evidence_class: str
    point_in_time: bool
    revised_fallback: bool


def derive_rrsfs_snapshot(
    *,
    as_of: str,
    rsafs_snapshot: PointInTimeSnapshot,
    cpi_snapshot: PointInTimeSnapshot,
) -> DerivedPointInTimeValue:
    """Derive RRSFS from same-as-of RSAFS and CPIAUCSL snapshots."""

    if rsafs_snapshot.as_of != cpi_snapshot.as_of:
        raise PointInTimeError("RRSFS derivation requires same as_of input snapshots")
    if not rsafs_snapshot.point_in_time or not cpi_snapshot.point_in_time:
        raise PointInTimeError("RRSFS derivation requires strict point-in-time inputs")
    if not rsafs_snapshot.observations or not cpi_snapshot.observations:
        raise PointInTimeError("RRSFS derivation requires non-empty input snapshots")
    rsafs_latest = rsafs_snapshot.observations[-1]
    cpi_by_month = {
        (obs.observation_date.year, obs.observation_date.month): obs
        for obs in cpi_snapshot.observations
    }
    cpi_latest = cpi_by_month.get(
        (rsafs_latest.observation_date.year, rsafs_latest.observation_date.month)
    )
    if cpi_latest is None:
        cpi_latest = cpi_snapshot.observations[-1]
    if cpi_latest.value == 0:
        raise PointInTimeError("CPIAUCSL value must be non-zero for RRSFS derivation")
    value = rsafs_latest.value / cpi_latest.value * 100.0
    availability = max(rsafs_latest.realtime_start, cpi_latest.realtime_start)
    return DerivedPointInTimeValue(
        series_id="RRSFS",
        as_of=as_of,
        selected_reference_month=_month_id(rsafs_latest.observation_date),
        value=value,
        formula_id="rrsfs_rsafs_deflated_by_cpiau_1982_84_100",
        formula_version="1",
        input_snapshot_ids=(
            f"RSAFS:{rsafs_latest.observation_date.isoformat()}:{rsafs_latest.realtime_start.isoformat()}",
            f"CPIAUCSL:{cpi_latest.observation_date.isoformat()}:{cpi_latest.realtime_start.isoformat()}",
        ),
        input_availability_dates=(
            rsafs_latest.realtime_start.isoformat(),
            cpi_latest.realtime_start.isoformat(),
        ),
        availability_date=availability.isoformat(),
        temporal_evidence_class="derived_point_in_time",
        point_in_time=True,
        revised_fallback=False,
    )


def _month_id(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"
