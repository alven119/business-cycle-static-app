from __future__ import annotations

from datetime import date

from business_cycle.indicators.point_in_time_derived import derive_rrsfs_snapshot
from business_cycle.data_sources.point_in_time import PointInTimeObservation, PointInTimeSnapshot


def make_snapshot(series_id: str, realtime_start: str, value: float) -> PointInTimeSnapshot:
    return PointInTimeSnapshot(
        series_id=series_id,
        as_of="2020-03-31",
        observations=[
            PointInTimeObservation(
                series_id=series_id,
                observation_date=date(2020, 2, 1),
                value=value,
                realtime_start=date.fromisoformat(realtime_start),
                realtime_end=date(9999, 12, 31),
                source="fixture",
                data_mode="vintage_as_of",
                availability_precision="day",
                fetched_at="2026-01-01T00:00:00Z",
                metadata={},
            )
        ],
        selection_mode="vintage_as_of",
        point_in_time=True,
        warnings=[],
    )


def test_rrsfs_derivation_outputs_provenance_but_contract_controls_strict_readiness() -> None:
    derived = derive_rrsfs_snapshot(
        as_of="2020-03-31",
        rsafs_snapshot=make_snapshot("RSAFS", "2020-03-15", 500000),
        cpi_snapshot=make_snapshot("CPIAUCSL", "2020-03-16", 250),
    )

    assert derived.temporal_evidence_class == "derived_point_in_time"
    assert derived.input_snapshot_ids
    assert derived.revised_fallback is False
