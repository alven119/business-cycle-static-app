from __future__ import annotations

from business_cycle.data_sources.census_retail_sales_pdf_parser import (
    parse_retail_sales_release_text,
)


def test_retail_parser_uses_modern_profile_for_recent_release() -> None:
    text = """
    FOR RELEASE AT 8:30 A.M. EDT, MONDAY, FEBRUARY 14, 2022
    Advance Monthly Retail Trade Survey
    Advance estimate of U.S. retail and food services sales for January 2022 was 650,000 million.
    The December 2021 revised retail sales estimate was 645,000 million.
    """

    result = parse_retail_sales_release_text(
        text,
        artifact_id="modern",
        source_checksum="abc",
        artifact_filename="adv2201.pdf",
    )

    assert result.parser_profile == "modern_2017_present"
    assert len(result.events) == 2
