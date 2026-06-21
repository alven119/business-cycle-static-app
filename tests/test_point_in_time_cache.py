from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def test_cache_atomic_write_and_read(tmp_path: Path) -> None:
    cache = PointInTimeCache(tmp_path)

    manifest = cache.write_series(
        "UNRATE",
        [
            {
                "series_id": "UNRATE",
                "observation_date": "2020-01-31",
                "value": "1.0",
                "realtime_start": "2020-02-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start="2020-01-01",
        observation_end="2020-12-31",
        as_of_start="2020-01-01",
        as_of_end="2020-12-31",
    )

    assert manifest["row_count"] == 1
    assert not list(tmp_path.glob("*.tmp"))
    assert cache.read_series("UNRATE").rows[0]["value"] == "1.0"


def test_cache_corruption_detection(tmp_path: Path) -> None:
    cache = PointInTimeCache(tmp_path)
    cache.write_series(
        "UNRATE",
        [
            {
                "series_id": "UNRATE",
                "observation_date": "2020-01-31",
                "value": "1.0",
                "realtime_start": "2020-02-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )
    cache.csv_path("UNRATE").write_text("corrupt", encoding="utf-8")

    with pytest.raises(PointInTimeCacheError):
        cache.read_series("UNRATE")


def test_cache_deduplicates_and_excludes_api_key(tmp_path: Path) -> None:
    cache = PointInTimeCache(tmp_path)
    row = {
        "series_id": "UNRATE",
        "observation_date": "2020-01-31",
        "value": "1.0",
        "realtime_start": "2020-02-15",
        "realtime_end": "9999-12-31",
    }
    cache.write_series(
        "UNRATE",
        [row, row],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    cached = cache.read_series("UNRATE")
    manifest_text = json.dumps(cached.manifest)
    assert len(cached.rows) == 1
    assert "FRED_API_KEY" not in manifest_text
    assert "api_key" not in manifest_text.lower()
