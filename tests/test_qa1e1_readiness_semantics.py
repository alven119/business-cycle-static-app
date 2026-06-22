from __future__ import annotations

from business_cycle.audits.point_in_time_coverage import _derived_output_pair_summary
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_provisional_derived_snapshot_is_not_strict_coverage(tmp_path) -> None:
    cache = PointInTimeCache(tmp_path)
    for series_id, value, realtime_start in [
        ("RSAFS", "500000", "2020-03-15"),
        ("CPIAUCSL", "250", "2020-03-16"),
    ]:
        cache.write_series(
            series_id,
            [
                {
                    "series_id": series_id,
                    "observation_date": "2020-02-01",
                    "value": value,
                    "realtime_start": realtime_start,
                    "realtime_end": "9999-12-31",
                }
            ],
            query_mode="vintage_as_of",
            observation_start=None,
            observation_end=None,
            as_of_start=None,
            as_of_end=None,
        )

    summary = _derived_output_pair_summary(
        cache=cache,
        derived_series_ids=["RRSFS"],
        as_of_dates=["2020-03-31"],
    )["RRSFS"]

    assert summary["candidate_pair_count"] == 1
    assert summary["strict_covered_pair_count"] == 0
    assert summary["strict_full_required_horizon_ready"] is False
