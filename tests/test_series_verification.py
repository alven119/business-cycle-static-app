from __future__ import annotations

from business_cycle.data_sources.base import DataProviderError, SeriesObservation
from business_cycle.indicators.series_verification import verify_catalog_series


class FakeProvider:
    def __init__(
        self,
        observations_by_series: dict[str, list[SeriesObservation]] | None = None,
        failures: dict[str, Exception] | None = None,
    ) -> None:
        self.observations_by_series = observations_by_series or {}
        self.failures = failures or {}

    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        if series_id in self.failures:
            raise self.failures[series_id]
        return self.observations_by_series.get(series_id, [])


def observations(series_id: str) -> list[SeriesObservation]:
    return [
        SeriesObservation(series_id=series_id, date="2020-02-01", value="2"),
        SeriesObservation(series_id=series_id, date="2020-01-01", value="1"),
    ]


def test_candidate_series_as_single_string() -> None:
    results = verify_catalog_series(
        [{"indicator_id": "x", "provider": "fred", "candidate_series": "UNRATE"}],
        {"fred": FakeProvider({"UNRATE": observations("UNRATE")})},
    )

    assert results[0].status == "ok"
    assert results[0].series_id == "UNRATE"


def test_candidate_series_as_list() -> None:
    results = verify_catalog_series(
        [
            {
                "indicator_id": "x",
                "provider": "fred",
                "candidate_series": [
                    {"provider": "fred", "series_id": "UNRATE"},
                    {"provider": "fred", "series_id": "ICSA"},
                ],
            }
        ],
        {
            "fred": FakeProvider(
                {
                    "UNRATE": observations("UNRATE"),
                    "ICSA": observations("ICSA"),
                }
            )
        },
    )

    assert [result.series_id for result in results] == ["UNRATE", "ICSA"]
    assert [result.status for result in results] == ["ok", "ok"]


def test_missing_candidate_series() -> None:
    results = verify_catalog_series([{"indicator_id": "x", "provider": "fred"}], {"fred": FakeProvider()})

    assert results[0].status == "missing_candidate_series"
    assert results[0].observations_count == 0


def test_provider_not_supported() -> None:
    results = verify_catalog_series(
        [{"indicator_id": "x", "provider": "yahoo", "candidate_series": "SPY"}],
        {"fred": FakeProvider()},
    )

    assert results[0].status == "provider_not_supported"
    assert results[0].provider == "yahoo"


def test_provider_download_failure_becomes_result() -> None:
    results = verify_catalog_series(
        [{"indicator_id": "x", "provider": "fred", "candidate_series": "BAD"}],
        {"fred": FakeProvider(failures={"BAD": DataProviderError("boom")})},
    )

    assert results[0].status == "download_failed"
    assert results[0].message == "boom"


def test_empty_observations() -> None:
    results = verify_catalog_series(
        [{"indicator_id": "x", "provider": "fred", "candidate_series": "EMPTY"}],
        {"fred": FakeProvider({"EMPTY": []})},
    )

    assert results[0].status == "empty_observations"
    assert results[0].observations_count == 0


def test_observations_status_ok_and_dates_are_correct() -> None:
    results = verify_catalog_series(
        [{"indicator_id": "x", "provider": "fred", "candidate_series": "UNRATE"}],
        {"fred": FakeProvider({"UNRATE": observations("UNRATE")})},
    )

    result = results[0]
    assert result.status == "ok"
    assert result.observations_count == 2
    assert result.first_date == "2020-01-01"
    assert result.last_date == "2020-02-01"


def test_one_indicator_failure_does_not_stop_other_verifications() -> None:
    results = verify_catalog_series(
        [
            {"indicator_id": "bad", "provider": "fred", "candidate_series": "BAD"},
            {"indicator_id": "good", "provider": "fred", "candidate_series": "UNRATE"},
        ],
        {
            "fred": FakeProvider(
                observations_by_series={"UNRATE": observations("UNRATE")},
                failures={"BAD": DataProviderError("bad series")},
            )
        },
    )

    assert [result.status for result in results] == ["download_failed", "ok"]

