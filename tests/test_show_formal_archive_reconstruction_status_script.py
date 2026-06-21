from __future__ import annotations

from pathlib import Path

import scripts.show_formal_archive_reconstruction_status as show_status
from business_cycle.storage.official_release_archive_cache import OfficialReleaseArchiveCache


def test_show_formal_archive_reconstruction_status_summarizes_cache(
    tmp_path: Path,
    capsys,
) -> None:
    cache = OfficialReleaseArchiveCache(tmp_path)
    cache.write_attempt(
        source_id="DCOILWTICO_eia_wti_spot_price_history",
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

    show_status.main(["--cache-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert "official_archive_cached_artifact_count=1" in output
    assert "official_archive_extracted_row_count=1" in output
    assert "archive_status series_id=DCOILWTICO" in output
