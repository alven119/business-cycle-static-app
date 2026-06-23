"""Phase 18 point-in-time input availability audit helpers."""

from __future__ import annotations

from typing import Any


def summarize_point_in_time_input_availability(
    *,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    scenario_count = len(rows)
    required_vintage_count = sum(row["required_vintage_count"] for row in rows)
    available_vintage_count = sum(row["available_vintage_count"] for row in rows)
    missing_vintage_count = sum(row["missing_vintage_count"] for row in rows)
    missing_input_count = sum(row["missing_input_count"] for row in rows)
    unavailable_input_count = sum(row["unavailable_input_count"] for row in rows)
    point_in_time_ready_row_count = sum(
        row["point_in_time_readiness_status"] == "metadata_ready_execution_disabled"
        for row in rows
    )
    return {
        "phase": "18",
        "point_in_time_input_availability_ready": (
            scenario_count > 0
            and point_in_time_ready_row_count == scenario_count
            and required_vintage_count == available_vintage_count
            and missing_vintage_count == 0
            and missing_input_count == 0
            and unavailable_input_count == 0
        ),
        "point_in_time_ready_row_count": point_in_time_ready_row_count,
        "required_vintage_count": required_vintage_count,
        "available_vintage_count": available_vintage_count,
        "missing_vintage_count": missing_vintage_count,
        "missing_input_count": missing_input_count,
        "unavailable_input_count": unavailable_input_count,
    }
