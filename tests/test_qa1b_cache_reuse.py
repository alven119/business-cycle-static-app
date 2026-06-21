from __future__ import annotations

from pathlib import Path

import scripts.update_point_in_time_data as updater
from business_cycle.data_sources.alfred_provider import AlfredObservation
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def _write_cache(cache: PointInTimeCache, series_id: str = "UNRATE") -> None:
    cache.write_series(
        series_id,
        [
            {
                "series_id": series_id,
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


def test_reuse_existing_avoids_api(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    cache = PointInTimeCache(tmp_path)
    _write_cache(cache)

    class ExplodingProvider:
        def fetch_observations(self, *_args: object, **_kwargs: object) -> list[AlfredObservation]:
            raise AssertionError("API should not be called")

    monkeypatch.setattr(updater, "AlfredProvider", ExplodingProvider)

    updater.main(["--series-id", "UNRATE", "--reuse-existing", "--cache-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert "cache_reused_series_count=1" in output
    assert "api_request_count=0" in output


def test_corrupt_cache_is_repaired_when_api_available(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    cache = PointInTimeCache(tmp_path)
    _write_cache(cache)
    cache.csv_path("UNRATE").write_text("corrupt", encoding="utf-8")

    class FakeProvider:
        last_request_count = 1
        last_pagination_count = 0

        def fetch_observations(self, series_id: str, **_kwargs: object) -> list[AlfredObservation]:
            return [
                AlfredObservation(
                    series_id=series_id,
                    observation_date="2020-01-31",
                    value="2.0",
                    realtime_start="2020-02-15",
                    realtime_end="9999-12-31",
                )
            ]

    monkeypatch.setattr(updater, "AlfredProvider", FakeProvider)

    updater.main(["--series-id", "UNRATE", "--reuse-existing", "--cache-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert "cache_written_series_count=1" in output
    assert PointInTimeCache(tmp_path).read_series("UNRATE").rows[0]["value"] == "2.0"
