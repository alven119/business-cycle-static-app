from __future__ import annotations

import pytest

from business_cycle.data_sources.census_release_calendar import (
    CensusReleaseCalendarError,
    parse_marts_release_calendar,
    summarize_required_month_coverage,
)


def test_marts_release_calendar_parses_structured_export_fixture() -> None:
    content = (
        "reference_month,official_release_date,official_release_time\n"
        "1998-01,1998-02-12,8:30 AM\n"
        "1998-02,1998-03-12,8:30 AM\n"
    ).encode()

    result = parse_marts_release_calendar(
        content,
        source_url="https://www.census.gov/retail/marts/www/MARTSreleasedates.xls",
        content_type="text/csv",
    )

    assert result.row_count == 2
    assert result.rows[0].reference_month == "1998-01"
    assert result.rows[0].official_release_date == "1998-02-12"
    assert result.rows[0].source_workbook_id == "MARTSreleasedates.xls"
    summary = summarize_required_month_coverage(
        result.rows,
        required_reference_months=["1998-01", "1998-03"],
    )
    assert summary["release_calendar_required_month_covered_count"] == 1
    assert summary["release_calendar_missing_required_month_count"] == 1
    assert summary["directory_mtime_used_as_release_date_count"] == 0


def test_marts_release_calendar_binary_xls_fails_closed_without_mtime_fallback() -> None:
    with pytest.raises(CensusReleaseCalendarError):
        parse_marts_release_calendar(
            b"\xd0\xcf\x11\xe0binary-biff",
            source_url="https://www.census.gov/retail/marts/www/MARTSreleasedates.xls",
            content_type="application/vnd.ms-excel",
        )
