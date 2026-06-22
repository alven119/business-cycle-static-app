from __future__ import annotations

from business_cycle.data_sources.census_retail_sales_pdf_parser import (
    CensusRetailPdfParseError,
    parse_retail_sales_release_text,
)


RETAIL_TEXT = """
FOR RELEASE AT 8:30 A.M. EDT, FRIDAY, FEBRUARY 13, 1998
Advance Monthly Retail Trade Survey
Advance estimate of U.S. retail and food services sales for January 1998 was 215,000 million.
The December 1997 revised retail sales estimate was 214,000 million.
"""


def test_pdf_text_release_date_and_reference_month_extraction() -> None:
    result = parse_retail_sales_release_text(
        RETAIL_TEXT,
        artifact_id="rsafs_fixture",
        source_checksum="abc",
        artifact_filename="adv9801.pdf",
    )

    assert result.release_datetime.startswith("1998-02-13")
    assert result.reference_month == "1998-01"
    assert result.parser_profile == "legacy_2000_2008"
    assert result.advance_estimate_count == 1
    assert result.revised_estimate_count == 1


def test_filename_reference_month_mismatch_fails_closed() -> None:
    try:
        parse_retail_sales_release_text(
            RETAIL_TEXT,
            artifact_id="rsafs_fixture",
            source_checksum="abc",
            artifact_filename="adv9802.pdf",
        )
    except CensusRetailPdfParseError as exc:
        assert "filename reference month" in str(exc)
    else:  # pragma: no cover - explicit failure readability
        raise AssertionError("mismatched filename/body reference month must fail closed")
