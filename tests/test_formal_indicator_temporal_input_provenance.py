from __future__ import annotations

from pathlib import Path

from business_cycle.audits.formal_indicator_temporal_inputs import (
    explain_formal_indicator_temporal_inputs,
)
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_temporal_input_provenance_uses_direct_exact_vintage_without_ambiguity(
    tmp_path: Path,
) -> None:
    catalog = tmp_path / "catalog.yaml"
    cache_dir = tmp_path / "cache"
    catalog.write_text(
        """
indicators:
  - indicator_id: real_retail_sales
    provider: fred
    candidate_series:
      - provider: fred
        series_id: RRSFS
      - provider: fred
        series_id: RSAFS
    score_method: level_percentile_score
    direction: higher_is_better
    parameters:
      min_periods: 1
    stale_after_days: 45
""",
        encoding="utf-8",
    )
    PointInTimeCache(cache_dir).write_series(
        "RRSFS",
        [
            {
                "series_id": "RRSFS",
                "observation_date": "2008-08-01",
                "value": "180000",
                "realtime_start": "2008-09-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    summary = explain_formal_indicator_temporal_inputs(
        as_of="2008-09-30",
        catalog_path=catalog,
        cache_dir=cache_dir,
    )

    item = summary["indicators"][0]
    assert summary["strict_score_without_covered_dependency_count"] == 0
    assert summary["strict_score_without_temporal_provenance_count"] == 0
    assert summary["direct_derived_dependency_ambiguity_count"] == 0
    assert summary["proxy_used_count"] == 0
    assert summary["revised_fallback_used_count"] == 0
    assert item["strict_output_ready"] is True
    assert item["dependency_series_ids"] == ["RRSFS", "RSAFS"]
    assert item["direct_or_derived"] == "direct"
    assert item["temporal_evidence_class"] == "exact_vintage_interval"
    assert item["source_artifact_ids"][0].startswith("pit_cache:RRSFS:")
    assert item["selected_observation_dates"] == ["2008-08-01"]
    assert item["availability_dates"] == ["2008-09-15"]


def test_temporal_input_provenance_fail_closed_without_strict_dependency(
    tmp_path: Path,
) -> None:
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(
        """
indicators:
  - indicator_id: real_retail_sales
    provider: fred
    candidate_series:
      - provider: fred
        series_id: RRSFS
    score_method: level_percentile_score
    direction: higher_is_better
    parameters:
      min_periods: 1
    stale_after_days: 45
""",
        encoding="utf-8",
    )

    summary = explain_formal_indicator_temporal_inputs(
        as_of="2000-03-31",
        catalog_path=catalog,
        cache_dir=tmp_path / "cache",
    )

    item = summary["indicators"][0]
    assert summary["scored_indicator_count"] == 0
    assert summary["strict_score_without_covered_dependency_count"] == 0
    assert item["strict_output_ready"] is False
    assert item["direct_or_derived"] == "none"
    assert item["temporal_evidence_class"] is None
    assert item["proxy_used"] is False
    assert item["revised_fallback_used"] is False
