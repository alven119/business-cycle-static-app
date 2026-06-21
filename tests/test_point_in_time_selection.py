from __future__ import annotations

import pytest

from business_cycle.data_sources.point_in_time import (
    PointInTimeError,
    PointInTimeSnapshot,
    build_derived_snapshot,
    select_initial_release_only,
    select_release_lag_proxy,
    select_vintage_as_of,
)


ROWS = [
    {
        "series_id": "TEST",
        "observation_date": "2020-01-31",
        "value": "1.0",
        "realtime_start": "2020-02-15",
        "realtime_end": "2020-03-10",
    },
    {
        "series_id": "TEST",
        "observation_date": "2020-01-31",
        "value": "2.0",
        "realtime_start": "2020-03-11",
        "realtime_end": "9999-12-31",
    },
    {
        "series_id": "TEST",
        "observation_date": "2020-02-29",
        "value": "3.0",
        "realtime_start": "2020-04-01",
        "realtime_end": "9999-12-31",
    },
]


def test_strict_selector_rejects_realtime_start_after_as_of() -> None:
    snapshot = select_vintage_as_of(ROWS, series_id="TEST", as_of="2020-02-29")

    assert [observation.value for observation in snapshot.observations] == [1.0]


def test_as_of_inside_realtime_interval_selects_correct_vintage() -> None:
    snapshot = select_vintage_as_of(ROWS, series_id="TEST", as_of="2020-03-01")

    assert snapshot.observations[-1].value == 1.0


def test_as_of_after_realtime_end_does_not_select_old_revision() -> None:
    snapshot = select_vintage_as_of(ROWS, series_id="TEST", as_of="2020-03-31")

    assert snapshot.observations[-1].value == 2.0


def test_open_ended_realtime_end_is_handled() -> None:
    snapshot = select_vintage_as_of(ROWS, series_id="TEST", as_of="2020-12-31")

    assert snapshot.observations[-1].value == 3.0


def test_initial_release_is_semantically_separate() -> None:
    snapshot = select_initial_release_only(ROWS, series_id="TEST", as_of="2020-12-31")

    assert snapshot.point_in_time is False
    assert snapshot.observations[0].value == 1.0


def test_release_lag_proxy_is_not_point_in_time() -> None:
    snapshot = select_release_lag_proxy(
        [{"series_id": "TEST", "date": "2020-01-31", "value": "1.0"}],
        series_id="TEST",
        as_of="2020-03-15",
        release_lag_days=30,
    )

    assert snapshot.point_in_time is False
    assert snapshot.proxy_series == ("TEST",)


def test_missing_realtime_metadata_fails_closed() -> None:
    with pytest.raises(PointInTimeError):
        select_vintage_as_of(
            [{"series_id": "TEST", "date": "2020-01-31", "value": "1.0"}],
            series_id="TEST",
            as_of="2020-03-01",
        )


def test_derived_snapshot_uses_max_input_availability() -> None:
    left = select_vintage_as_of(ROWS, series_id="LEFT", as_of="2020-03-31")
    right = select_vintage_as_of(
        [
            {
                "series_id": "RIGHT",
                "observation_date": "2020-01-31",
                "value": "0.5",
                "realtime_start": "2020-02-20",
                "realtime_end": "9999-12-31",
            }
        ],
        series_id="RIGHT",
        as_of="2020-03-31",
    )

    snapshot = build_derived_snapshot(
        derived_series_id="derived:TEST",
        input_snapshots=[left, right],
    )

    assert snapshot.observations[0].realtime_start.isoformat() == "2020-03-11"


def test_derived_snapshot_rejects_non_strict_input() -> None:
    strict = select_vintage_as_of(ROWS, series_id="LEFT", as_of="2020-03-31")
    non_strict = PointInTimeSnapshot(
        series_id="RIGHT",
        as_of=strict.as_of,
        observations=(),
        selection_mode="revised",
        point_in_time=False,
    )

    with pytest.raises(PointInTimeError):
        build_derived_snapshot(
            derived_series_id="derived:TEST",
            input_snapshots=[strict, non_strict],
        )
