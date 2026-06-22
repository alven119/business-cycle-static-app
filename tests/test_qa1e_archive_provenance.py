from business_cycle.storage.official_release_archive_cache import OfficialReleaseArchiveCache


def test_official_archive_artifact_requires_checksum_and_parser_version(tmp_path) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)
    metadata = cache.write_attempt(
        source_id="DCOILWTICO_eia",
        source_domain="eia.gov",
        artifact_url="https://www.eia.gov/dnav/pet/hist/RWTCD.htm",
        artifact_type="official_observational_archive_candidate",
        release_date="2026-06-17",
        reference_period=None,
        parser_id="eia",
        parser_version="1",
        parse_status="parsed",
        extracted_row_count=1,
        content=b"official",
        network_attempted=True,
        http_status=200,
        implementation_status="implemented_parser_candidate",
    )

    assert metadata["checksum"]
    assert metadata["parser_version"] == "1"
    assert metadata["parsed_row_count"] == 1
