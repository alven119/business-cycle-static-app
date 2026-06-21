from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.storage.official_release_archive_cache import (
    OfficialReleaseArchiveCache,
    OfficialReleaseArchiveCacheError,
)


def test_official_release_archive_cache_writes_metadata_atomically(tmp_path: Path) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)

    metadata = cache.write_attempt(
        source_id="DGS10_h15",
        source_domain="federalreserve.gov",
        artifact_url="https://www.federalreserve.gov/releases/h15/",
        artifact_type="official_release_archive_candidate",
        release_date=None,
        reference_period=None,
        parser_id="test_parser",
        parser_version="1",
        parse_status="blocked_pending_parser",
        extracted_row_count=0,
        network_attempted=False,
    )

    assert metadata["source_id"] == "DGS10_h15"
    assert metadata["no_secret"] is True
    assert metadata["extracted_row_count"] == 0
    assert metadata["placeholder_only"] is True
    assert cache.read("DGS10_h15").metadata["checksum"]


def test_official_release_archive_cache_records_real_artifact_metadata(tmp_path: Path) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)

    metadata = cache.write_attempt(
        source_id="DCOILWTICO_eia",
        source_domain="eia.gov",
        artifact_url="https://www.eia.gov/dnav/pet/hist/RWTCD.htm",
        artifact_type="official_observational_archive_candidate",
        release_date="2026-06-17",
        reference_period=None,
        parser_id="eia_parser",
        parser_version="1",
        parse_status="parsed",
        extracted_row_count=2,
        content=b"official artifact",
        source_type="official_observational_archive",
        content_type="text/html",
        network_attempted=True,
        http_status=200,
        implementation_status="implemented_parser_candidate",
    )

    assert metadata["artifact_id"] == "DCOILWTICO_eia"
    assert metadata["content_file"] == "DCOILWTICO_eia.artifact"
    assert metadata["parsed_row_count"] == 2
    assert metadata["placeholder_only"] is False
    assert cache.read("DCOILWTICO_eia").content_path is not None


def test_official_release_archive_cache_rejects_secret_metadata(tmp_path: Path) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)

    with pytest.raises(OfficialReleaseArchiveCacheError):
        cache.write_attempt(
            source_id="bad",
            source_domain="fred.stlouisfed.org",
            artifact_url="https://fred.stlouisfed.org/?api_key=secret",
            artifact_type="official_release_archive_candidate",
            release_date=None,
            reference_period=None,
            parser_id="test_parser",
            parser_version="1",
            parse_status="blocked",
            extracted_row_count=0,
        )
