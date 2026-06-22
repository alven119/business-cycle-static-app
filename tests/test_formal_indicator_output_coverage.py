from __future__ import annotations

from pathlib import Path

from business_cycle.audits.formal_indicator_output_coverage import (
    summarize_formal_indicator_output_coverage,
)
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_formal_indicator_output_coverage_counts_indicator_pairs(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.yaml"
    scenarios = tmp_path / "scenarios.yaml"
    cache_dir = tmp_path / "cache"
    catalog.write_text(
        """
indicators:
  - indicator_id: unemployment_rate
    provider: fred
    candidate_series:
      - provider: fred
        series_id: UNRATE
    score_method: level_percentile_score
    direction: lower_is_better
    parameters:
      min_periods: 1
    stale_after_days: 45
""",
        encoding="utf-8",
    )
    scenarios.write_text(
        """
scenarios:
  - scenario_id: fixture
    window_start: '2020-03-01'
    window_end: '2020-03-31'
""",
        encoding="utf-8",
    )
    PointInTimeCache(cache_dir).write_series(
        "UNRATE",
        [
            {
                "series_id": "UNRATE",
                "observation_date": "2020-02-01",
                "value": "4.0",
                "realtime_start": "2020-03-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    summary = summarize_formal_indicator_output_coverage(
        catalog_path=catalog,
        scenarios_path=scenarios,
        cache_dir=cache_dir,
    )

    assert summary["formal_indicator_output_total_pair_count"] == 1
    assert summary["formal_indicator_output_covered_pair_count"] == 1
    assert summary["formal_indicator_output_missing_pair_count"] == 0
    assert summary["formal_indicator_output_counting_ready"] is True
