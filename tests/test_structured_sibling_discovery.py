from __future__ import annotations

from business_cycle.data_sources.structured_sibling_discovery import probe_structured_siblings


def test_structured_sibling_discovery_prefers_existing_official_sibling() -> None:
    seen: list[str] = []

    def exists(url: str) -> bool:
        seen.append(url)
        return url.endswith(".xls")

    summary = probe_structured_siblings(
        ["https://www2.census.gov/retail/releases/historical/marts/adv9801.pdf"],
        exists=exists,
    )

    assert summary.required_release_count == 1
    assert summary.structured_sibling_found_count == 1
    assert summary.xls_found_count == 1
    assert summary.image_pdf_only_count == 0
    assert seen == ["https://www2.census.gov/retail/releases/historical/marts/adv9801.xls"]


def test_structured_sibling_discovery_marks_image_pdf_only_when_none_exist() -> None:
    summary = probe_structured_siblings(
        ["https://www2.census.gov/retail/releases/historical/marts/adv9801.pdf"],
        exists=lambda _url: False,
    )

    assert summary.structured_sibling_found_count == 0
    assert summary.image_pdf_only_count == 1
    assert summary.unresolved_artifact_count == 1
