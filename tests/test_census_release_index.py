from __future__ import annotations

from business_cycle.data_sources.census_release_index import parse_census_release_index


def test_census_release_index_separates_direct_artifacts_and_landing_pages() -> None:
    html = """
    <a href="/retail/marts/historic_releases.html">Data landing</a>
    <a href="https://www2.census.gov/retail/releases/historical/marts/adv9801.pdf">January 1998</a>
    <a href="https://www2.census.gov/retail/releases/historical/marts/adv9801.pdf">January 1998</a>
    <a href="https://example.com/not-official.csv">January 1998</a>
    """

    items, summary = parse_census_release_index(
        release_family="RSAFS",
        landing_page_url="https://www.census.gov/retail/marts/historic_releases.html",
        html=html,
    )

    assert summary.census_release_index_page_count == 1
    assert summary.census_release_link_count == 2
    assert summary.census_direct_artifact_link_count == 1
    assert summary.census_landing_page_only_count == 1
    assert summary.census_duplicate_release_link_count == 1
    assert items[1].artifact_type == "pdf"
    assert items[1].reference_period == "1998-01"
    assert items[1].release_date is None
