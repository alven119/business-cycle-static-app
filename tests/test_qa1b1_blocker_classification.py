from __future__ import annotations

from pathlib import Path

from business_cycle.audits import point_in_time_coverage as coverage
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_missing_key_is_environment_blocker_not_qa1c(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["blocker_class"] == "environment_configuration_blocked"
    assert summary["official_query_attempted_series_count"] == 0
    assert summary["live_verified_unsupported_series_count"] == 0
    assert summary["recommended_next_phase"] == "QA1B.1_RETRY"


def test_key_present_but_no_official_query_is_retry_not_qa1c(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["blocker_class"] == "official_query_not_attempted"
    assert summary["official_query_attempted_series_count"] == 0
    assert summary["live_verified_unsupported_series_count"] == 0
    assert summary["recommended_next_phase"] == "QA1B.1_RETRY"


def test_registry_declared_exact_is_separate_from_live_verified_cache(
    tmp_path: Path,
    monkeypatch,
) -> None:
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

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["registry_declared_exact_vintage_series_count"] == 37
    assert summary["live_verified_exact_vintage_series_count"] == 1
    assert summary["official_query_attempted_series_count"] == 1


def test_live_verified_partial_history_recommends_qa1c(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    cache = PointInTimeCache(tmp_path)
    cache.write_series(
        "DGS10",
        [
            {
                "series_id": "DGS10",
                "observation_date": "2004-01-01",
                "value": "4.25",
                "realtime_start": "2005-06-28",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start="2004-01-01",
        observation_end="2005-12-31",
        as_of_start="1776-07-04",
        as_of_end="2005-12-31",
    )

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["blocker_class"] == "official_history_insufficient"
    assert summary["live_verified_history_insufficient_series_count"] == 1
    assert summary["recommended_next_phase"] == "QA1C"
