from __future__ import annotations

from business_cycle.data_sources.census_retail_sales_archive import (
    parse_retail_sales_text_events,
    select_retail_release_event_as_of,
)


TEXT = """
FOR RELEASE AT 8:30 A.M. EDT, FRIDAY, FEBRUARY 13, 1998
Advance Monthly Retail Trade Survey
Advance estimate of U.S. retail and food services sales for January 1998 was 215,000 million.
The December 1997 revised retail sales estimate was 214,000 million.
"""


def test_retail_release_events_are_not_visible_before_release() -> None:
    events = parse_retail_sales_text_events(
        TEXT,
        artifact_id="fixture",
        source_checksum="abc",
        artifact_filename="adv9801.pdf",
    )

    before = select_retail_release_event_as_of(events, as_of="1998-02-12")
    after = select_retail_release_event_as_of(events, as_of="1998-02-13")

    assert before.point_in_time is False
    assert before.future_event_blocked_count > 0
    assert after.point_in_time is True
    assert after.selected_reference_month == "1998-01"
    assert after.selected_estimate_stage == "advance"
    assert after.source_artifact_id == "fixture"
    assert after.parser_version == "1"


def test_retail_revision_is_visible_only_after_revision_release() -> None:
    events = parse_retail_sales_text_events(
        TEXT,
        artifact_id="fixture",
        source_checksum="abc",
        artifact_filename="adv9801.pdf",
    )

    selected = select_retail_release_event_as_of(
        events,
        as_of="1998-02-13",
        reference_month="1997-12",
    )

    assert selected.point_in_time is True
    assert selected.selected_estimate_stage == "revised"
    assert selected.value == 214000.0
