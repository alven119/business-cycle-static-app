from __future__ import annotations

from business_cycle.validation.point_in_time_input_availability import (
    summarize_point_in_time_input_availability,
)


def test_point_in_time_input_availability_requires_complete_metadata() -> None:
    rows = [
        {
            "required_vintage_count": 1,
            "available_vintage_count": 1,
            "missing_vintage_count": 0,
            "missing_input_count": 0,
            "unavailable_input_count": 0,
            "point_in_time_readiness_status": "metadata_ready_execution_disabled",
        }
    ]

    summary = summarize_point_in_time_input_availability(rows=rows)

    assert summary["point_in_time_input_availability_ready"] is True
    assert summary["point_in_time_ready_row_count"] == 1
    assert summary["required_vintage_count"] == 1
    assert summary["available_vintage_count"] == 1
    assert summary["missing_vintage_count"] == 0


def test_point_in_time_input_availability_rejects_missing_vintage() -> None:
    rows = [
        {
            "required_vintage_count": 1,
            "available_vintage_count": 0,
            "missing_vintage_count": 1,
            "missing_input_count": 0,
            "unavailable_input_count": 0,
            "point_in_time_readiness_status": "metadata_ready_execution_disabled",
        }
    ]

    summary = summarize_point_in_time_input_availability(rows=rows)

    assert summary["point_in_time_input_availability_ready"] is False
    assert summary["missing_vintage_count"] == 1
