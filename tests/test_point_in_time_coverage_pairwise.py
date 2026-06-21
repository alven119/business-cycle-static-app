from business_cycle.audits.point_in_time_coverage import _dgs10_pair_summary


def test_dgs10_pair_summary_distinguishes_partial_from_full_horizon() -> None:
    summary = _dgs10_pair_summary(
        {
            "DGS10": {
                "required_pair_count": 10,
                "covered_pair_count": 6,
                "missing_pair_count": 4,
                "first_covered_as_of": "2005-07-31",
                "last_covered_as_of": "2021-12-31",
                "first_missing_as_of": "1998-01-31",
                "last_missing_as_of": "2005-06-30",
            }
        }
    )

    assert summary["dgs10_partial_horizon_ready"] is True
    assert summary["dgs10_full_required_horizon_ready"] is False
    assert summary["dgs10_covered_pair_count"] == 6
