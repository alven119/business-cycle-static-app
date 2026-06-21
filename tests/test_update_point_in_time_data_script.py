from __future__ import annotations

from pathlib import Path

import scripts.update_point_in_time_data as updater
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_updater_dry_run_does_not_call_api_or_write(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    exit_code = updater.main(
        [
            "--series-id",
            "UNRATE",
            "--dry-run",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert not any(tmp_path.iterdir())


def test_updater_no_api_reuses_existing_cache(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
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

    exit_code = updater.main(
        [
            "--series-id",
            "UNRATE",
            "--no-api",
            "--reuse-existing",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
