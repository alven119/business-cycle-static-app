from datetime import date

from business_cycle.data_sources.point_in_time import PointInTimeObservation, PointInTimeSnapshot
from business_cycle.indicators.point_in_time_derived import derive_rrsfs_snapshot


def _snapshot(series_id: str, value: float) -> PointInTimeSnapshot:
    return PointInTimeSnapshot(
        series_id=series_id,
        as_of=date.fromisoformat("2020-03-31"),
        observations=(
            PointInTimeObservation(
                series_id=series_id,
                observation_date=date.fromisoformat("2020-02-01"),
                value=value,
                realtime_start=date.fromisoformat("2020-03-15"),
                realtime_end=None,
                source="alfred",
                data_mode="vintage_as_of",
                availability_precision="day",
                fetched_at="2026-06-22T00:00:00+00:00",
            ),
        ),
        selection_mode="vintage_as_of",
        point_in_time=True,
    )


def test_rrsfs_formula_uses_rsafs_deflated_by_cpi() -> None:
    value = derive_rrsfs_snapshot(
        as_of="2020-03-31",
        rsafs_snapshot=_snapshot("RSAFS", 500000.0),
        cpi_snapshot=_snapshot("CPIAUCSL", 250.0),
    )

    assert value.series_id == "RRSFS"
    assert value.value == 200000.0
    assert value.temporal_evidence_class == "derived_point_in_time"
    assert value.revised_fallback is False
