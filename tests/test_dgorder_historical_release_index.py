from __future__ import annotations

from business_cycle.data_sources.census_release_index import parse_census_release_index


def test_dgorder_historical_release_index_extracts_filename_reference_candidate() -> None:
    html = """
    <a href="/manufacturing/m3/historical_data/pressreleases/prel/1998/jan98prel.pdf">
      January 1998 advance report
    </a>
    """

    items, summary = parse_census_release_index(
        release_family="DGORDER",
        landing_page_url="https://www.census.gov/manufacturing/m3/historical_data/index.html",
        html=html,
    )

    assert summary.census_direct_artifact_link_count == 1
    assert items[0].artifact_type == "pdf"
    assert items[0].reference_month_candidate == "1998-01"
    assert items[0].release_date is None
    assert items[0].last_modified_used_as_release_date is False
