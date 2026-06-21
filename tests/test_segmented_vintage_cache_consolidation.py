from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.storage.point_in_time_cache import (
    PointInTimeCache,
    PointInTimeCacheError,
    merge_point_in_time_rows,
)


def _row(value: str = "1.0") -> dict[str, str]:
    return {
        "series_id": "DGS10",
        "observation_date": "2008-09-30",
        "value": value,
        "realtime_start": "2008-10-01",
        "realtime_end": "9999-12-31",
    }


def test_segmented_merge_deduplicates_identical_rows() -> None:
    rows = merge_point_in_time_rows("DGS10", [[_row()], [_row()]])

    assert len(rows) == 1
    assert rows[0]["value"] == "1.0"


def test_segmented_merge_rejects_conflicting_duplicate_values() -> None:
    with pytest.raises(PointInTimeCacheError):
        merge_point_in_time_rows("DGS10", [[_row("1.0")], [_row("2.0")]])


def test_consolidated_segmented_cache_rebuilds_manifest(tmp_path: Path) -> None:
    cache = PointInTimeCache(tmp_path)

    manifest = cache.consolidate_segmented_vintage_cache(
        "DGS10",
        [[_row()], [_row()]],
        query_mode="vintage_as_of_realtime_periods",
        observation_start="2005-06-28",
        observation_end="2021-12-31",
        as_of_start="2005-06-28",
        as_of_end="2021-12-31",
        segment_metadata=[
            {"realtime_start": "2005-06-28", "realtime_end": "2009-12-31"},
            {"realtime_start": "2010-01-01", "realtime_end": "2014-12-31"},
        ],
    )

    cached = cache.read_series("DGS10")
    assert manifest["row_count"] == 1
    assert cached.manifest["segmented_cache"] is True
    assert cached.manifest["segment_count"] == 2
    assert cached.manifest["earliest_observation_date"] == "2008-09-30"
    assert cached.manifest["segment_merge_failure_count"] == 0


def test_failed_segmented_merge_preserves_existing_cache(tmp_path: Path) -> None:
    cache = PointInTimeCache(tmp_path)
    cache.write_series(
        "DGS10",
        [_row("1.0")],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    with pytest.raises(PointInTimeCacheError):
        cache.consolidate_segmented_vintage_cache(
            "DGS10",
            [[_row("2.0"), _row("3.0")]],
            query_mode="vintage_as_of_realtime_periods",
            observation_start=None,
            observation_end=None,
            as_of_start=None,
            as_of_end=None,
            segment_metadata=[],
            force=True,
        )

    assert cache.read_series("DGS10").rows[0]["value"] == "1.0"
