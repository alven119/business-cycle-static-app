from __future__ import annotations

from pathlib import Path

import scripts.update_point_in_time_data as updater
from business_cycle.data_sources.alfred_provider import AlfredObservation
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


def test_updater_single_series_smoke_writes_cache_and_efficiency_summary(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")

    class FakeProvider:
        last_request_count = 1
        last_pagination_count = 0

        def fetch_observations(self, series_id: str, **_kwargs: object) -> list[AlfredObservation]:
            return [
                AlfredObservation(
                    series_id=series_id,
                    observation_date="2020-01-31",
                    value="1.0",
                    realtime_start="2020-02-15",
                    realtime_end="9999-12-31",
                )
            ]

    monkeypatch.setattr(updater, "AlfredProvider", FakeProvider)

    exit_code = updater.main(
        [
            "--series-id",
            "UNRATE",
            "--scenario-horizons",
            "--reuse-existing",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "fred_api_key_present=true" in output
    assert "cache_written_series_count=1" in output
    assert "per_as_of_network_request_count=0" in output
    assert "monthly_as_of_network_loop_detected=false" in output
    assert PointInTimeCache(tmp_path).read_series("UNRATE").manifest["row_count"] == 1
