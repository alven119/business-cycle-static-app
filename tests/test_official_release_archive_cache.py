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
    )

    assert metadata["source_id"] == "DGS10_h15"
    assert metadata["no_secret"] is True
    assert metadata["extracted_row_count"] == 0
    assert cache.read("DGS10_h15").metadata["checksum"]


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
