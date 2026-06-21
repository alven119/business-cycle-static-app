from __future__ import annotations

from business_cycle.data_sources.point_in_time import select_vintage_as_of


def test_later_snapshot_ready_even_when_early_history_missing() -> None:
    rows = [
        {
            "series_id": "DGS10",
            "observation_date": "2008-09-29",
            "value": "3.85",
            "realtime_start": "2008-09-30",
            "realtime_end": "9999-12-31",
        }
    ]

    early = select_vintage_as_of(rows, series_id="DGS10", as_of="2000-03-31")
    later = select_vintage_as_of(rows, series_id="DGS10", as_of="2008-09-30")

    assert not early.observations
    assert later.observations
    assert later.observations[-1].observation_date.isoformat() == "2008-09-29"
