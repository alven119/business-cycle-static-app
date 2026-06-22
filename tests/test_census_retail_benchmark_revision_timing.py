from __future__ import annotations

from business_cycle.data_sources.census_release_event_store import select_latest_census_event_as_of
from business_cycle.data_sources.census_retail_sales_pdf_parser import RetailReleaseEvent


def test_benchmark_revision_is_not_visible_before_release_date() -> None:
    events = [
        RetailReleaseEvent(
            event_id="RSAFS|1998-01|advance|1998-02-13|a",
            series_id="RSAFS",
            release_datetime="1998-02-13T08:30:00",
            availability_date="1998-02-13",
            reference_month="1998-01",
            estimate_stage="advance",
            value=215000.0,
            unit="millions_of_dollars",
            seasonal_adjustment="seasonally_adjusted",
            source_artifact_id="a",
            source_checksum="abc",
            parser_profile="legacy_2000_2008",
        ),
        RetailReleaseEvent(
            event_id="RSAFS|1998-01|benchmark_revision|1999-04-01|b",
            series_id="RSAFS",
            release_datetime="1999-04-01T08:30:00",
            availability_date="1999-04-01",
            reference_month="1998-01",
            estimate_stage="benchmark_revision",
            value=216000.0,
            unit="millions_of_dollars",
            seasonal_adjustment="seasonally_adjusted",
            source_artifact_id="b",
            source_checksum="def",
            parser_profile="legacy_2000_2008",
        ),
    ]

    before = select_latest_census_event_as_of(
        events,
        series_id="RSAFS",
        as_of="1999-03-31",
        reference_month="1998-01",
    )
    after = select_latest_census_event_as_of(
        events,
        series_id="RSAFS",
        as_of="1999-04-01",
        reference_month="1998-01",
    )

    assert before.selected_estimate_stage == "advance"
    assert before.value == 215000.0
    assert after.selected_estimate_stage == "benchmark_revision"
    assert after.benchmark_revision_applied is True
