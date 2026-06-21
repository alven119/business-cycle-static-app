from __future__ import annotations

from pathlib import Path

from business_cycle.audits.point_in_time_coverage import _archive_progress_summary
from business_cycle.storage.official_release_archive_cache import OfficialReleaseArchiveCache


def test_archive_progress_counters_do_not_create_strict_coverage(tmp_path: Path) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)
    cache.write_attempt(
        source_id="DCOILWTICO_eia",
        source_domain="eia.gov",
        artifact_url="https://www.eia.gov/dnav/pet/hist/RWTCD.htm",
        artifact_type="official_observational_archive_candidate",
        release_date="2026-06-17",
        reference_period=None,
        parser_id="eia",
        parser_version="1",
        parse_status="parsed",
        extracted_row_count=2,
        content=b"official",
        network_attempted=True,
        http_status=200,
        implementation_status="implemented_parser_candidate",
    )

    summary = _archive_progress_summary(cache)

    assert summary["official_archive_extracted_row_count"] == 2
    assert summary["implemented_archive_entry_without_parsed_rows_count"] == 0
