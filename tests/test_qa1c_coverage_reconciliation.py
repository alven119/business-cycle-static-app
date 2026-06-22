from __future__ import annotations

from pathlib import Path

from business_cycle.audits import point_in_time_coverage as coverage
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_partial_vintage_support_is_not_full_horizon_ready(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    monkeypatch.setattr(
        coverage,
        "scenario_month_end_dates",
        lambda _path: ["2004-12-31", "2008-09-30"],
    )
    cache = PointInTimeCache(tmp_path)
    cache.write_series(
        "DGS10",
        [
            {
                "series_id": "DGS10",
                "observation_date": "2008-09-29",
                "value": "3.85",
                "realtime_start": "2008-09-30",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start="2004-01-01",
        observation_end="2008-12-31",
        as_of_start="1776-07-04",
        as_of_end="2008-12-31",
    )

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["official_query_supported_series_count"] == 1
    assert summary["partial_vintage_history_series_count"] == 1
    assert summary["full_required_horizon_exact_vintage_series_count"] == 0
    assert summary["full_required_horizon_strict_ready_series_count"] == 0
    assert summary["unresolved_formal_series_count"] == 16
    assert summary["formal_derived_missing_dependency_series_ids"] == ["RRSFS"]
