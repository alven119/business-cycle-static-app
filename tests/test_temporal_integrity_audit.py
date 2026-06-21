from __future__ import annotations

from business_cycle.audits import filter_point_in_time_records, summarize_temporal_integrity


def test_post_release_leakage_is_excluded() -> None:
    result = filter_point_in_time_records(
        [
            {
                "series_id": "real_retail_sales",
                "observation_date": "2020-01-31",
                "available_at": "2020-02-15",
                "vintage_date": "2020-02-15",
                "value": 1.0,
            }
        ],
        as_of="2020-01-31",
    )

    assert not result.included_records
    assert result.excluded_records[0]["excluded_reason"] == "post_release"


def test_post_as_of_revision_is_excluded() -> None:
    result = filter_point_in_time_records(
        [
            {
                "series_id": "initial_jobless_claims",
                "observation_date": "2020-01-01",
                "available_at": "2020-01-05",
                "vintage_date": "2020-02-01",
                "value": 1.0,
            }
        ],
        as_of="2020-01-31",
    )

    assert not result.included_records
    assert result.excluded_records[0]["excluded_reason"] == "post_as_of_revision"


def test_missing_availability_metadata_blocks_record() -> None:
    result = filter_point_in_time_records(
        [{"series_id": "imports_goods_services", "observation_date": "2020-01-31"}],
        as_of="2020-02-29",
    )

    assert result.blocked_records
    assert result.blocked_records[0]["blocked_reason"] == "missing_availability_metadata"


def test_temporal_integrity_summary_blocks_point_in_time_claim() -> None:
    summary = summarize_temporal_integrity()

    assert summary["audited_series_count"] >= 8
    assert summary["series_with_release_lag_count"] >= 8
    assert summary["availability_metadata_complete_count"] == summary["audited_series_count"]
    assert summary["series_missing_availability_metadata_count"] == 0
    assert summary["release_lag_proxy_misclassified_as_point_in_time_count"] == 0
    assert summary["revised_data_only"] is False
    assert summary["vintage_data_supported"] is True
    assert summary["point_in_time_backtest_ready"] is False
    assert summary["temporal_leakage_blocker_count"] == 0
