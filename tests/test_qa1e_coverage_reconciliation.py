from business_cycle.audits.point_in_time_coverage import (
    _derived_output_pair_summary,
    _recommended_next_phase,
)
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_derived_output_pair_summary_requires_both_inputs(tmp_path) -> None:
    cache = PointInTimeCache(tmp_path)
    cache.write_series(
        "RSAFS",
        [
            {
                "series_id": "RSAFS",
                "observation_date": "2020-02-01",
                "value": "500000",
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

    summary = _derived_output_pair_summary(
        cache=cache,
        derived_series_ids=["RRSFS"],
        as_of_dates=["2020-03-31"],
    )

    assert summary["RRSFS"]["covered_pair_count"] == 0
    assert summary["RRSFS"]["missing_pair_count"] == 1


def test_qa1e_review_recommended_after_archive_attempts_remain_blocked() -> None:
    assert (
        _recommended_next_phase(
            formal_ready=False,
            blocker_class="official_history_insufficient",
            official_archive_parse_attempted_count=1,
        )
        == "QA1E_REVIEW"
    )
