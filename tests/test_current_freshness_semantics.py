from __future__ import annotations

from business_cycle.current.current_freshness_semantics import (
    summarize_current_freshness_semantics,
)


def test_frequency_aware_freshness_does_not_count_missing_as_stale() -> None:
    manifest = {
        "snapshot_as_of": "2026-06-26",
        "data_mode": "revised_live_current",
        "live_fetch_succeeded": True,
        "cache_used": False,
        "fixture_used": False,
        "requested_series_count": 4,
        "fetched_series_count": 3,
        "stale_series_count_before": 4,
        "manifest_hash": "fixture",
        "series_refresh_rows": [
            {
                "series_id": "MONTHLY",
                "source": "FRED/ALFRED",
                "frequency": "monthly",
                "release_family": "fixture monthly",
                "source_mode": "live_revised",
                "latest_observation_date": "2026-05-01",
                "point_in_time_eligible": True,
                "release_lag_metadata_complete": True,
            },
            {
                "series_id": "QUARTERLY",
                "source": "FRED/ALFRED",
                "frequency": "quarterly",
                "release_family": "fixture quarterly",
                "source_mode": "live_revised",
                "latest_observation_date": "2026-01-01",
                "point_in_time_eligible": True,
                "release_lag_metadata_complete": True,
            },
            {
                "series_id": "OLD",
                "source": "FRED/ALFRED",
                "frequency": "monthly",
                "release_family": "fixture monthly",
                "source_mode": "live_revised",
                "latest_observation_date": "2026-03-01",
                "point_in_time_eligible": True,
                "release_lag_metadata_complete": True,
            },
            {
                "series_id": "MISSING",
                "source": "FRED/ALFRED",
                "frequency": "monthly",
                "release_family": "fixture monthly",
                "source_mode": "unsupported",
                "latest_observation_date": "unknown",
                "point_in_time_eligible": False,
                "release_lag_metadata_complete": False,
            },
        ],
    }

    summary = summarize_current_freshness_semantics(refresh_manifest=manifest)

    assert summary["freshness_semantics_ready"] is True
    assert summary["fresh_enough_series_count"] == 2
    assert summary["stale_series_count_after"] == 1
    assert summary["stale_series_count_after"] < summary["stale_series_count_before"]
    assert summary["missing_counted_as_stale_count"] == 0
    assert summary["unavailable_counted_as_stale_count"] == 0
    assert summary["source_disabled_counted_as_stale_count"] == 0
    assert summary["result"] == "passed"
