from __future__ import annotations

from pathlib import Path

from business_cycle.audits import point_in_time_coverage as coverage
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_current_repo_metadata_complete_but_cache_not_ready(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["discovered_unique_series_count"] == 38
    assert summary["availability_metadata_complete_count"] == 38
    assert summary["formal_indicator_count"] == 13
    assert summary["formal_phase_point_in_time_ready"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["blocker_class"] == "environment_configuration_blocked"
    assert summary["official_query_attempted_series_count"] == 0
    assert summary["registry_declared_exact_vintage_series_count"] == 37
    assert summary["live_verified_exact_vintage_series_count"] == 0
    assert summary["recommended_next_phase"] == "QA1B.1_RETRY"
    assert summary["formal_scenario_as_of_date_count"] == 228
    assert summary["formal_total_coverage_pair_count"] == 3420
    assert summary["formal_missing_pair_count"] == 3420


def test_formal_scenario_coverage_calculates_complete_ratio(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        coverage,
        "scenario_month_end_dates",
        lambda _path: ["2020-03-31"],
    )
    deps = coverage.discover_formal_dependencies("specs/indicator_catalog.yaml")
    cache = PointInTimeCache(tmp_path)
    for series_id in deps.direct_series_ids:
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

    summary = coverage.summarize_point_in_time_coverage(cache_dir=tmp_path)

    assert summary["formal_missing_vintage_dependency_count"] == 0
    assert summary["formal_scenario_as_of_date_count"] == 1
    assert summary["formal_total_coverage_pair_count"] == len(deps.direct_series_ids)
    assert summary["formal_covered_pair_count"] == len(deps.direct_series_ids)
    assert summary["formal_missing_pair_count"] == 0
    assert summary["formal_proxy_pair_count"] == 0
    assert summary["formal_initial_release_only_pair_count"] == 0
    assert summary["formal_revised_fallback_pair_count"] == 0
    assert summary["strict_snapshot_validation_failure_count"] == 0
    assert summary["formal_scenario_as_of_coverage_ratio"] == 1.0
    assert summary["formal_phase_point_in_time_ready"] is True
    assert summary["recommended_next_phase"] == "QA2"
