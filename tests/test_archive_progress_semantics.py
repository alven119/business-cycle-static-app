from __future__ import annotations

from pathlib import Path

import scripts.reconstruct_formal_official_archives as reconstruct
from business_cycle.data_sources.eia_wti_observational_archive import EiaWtiFetchResult, EiaWtiObservation


def test_placeholder_only_entries_are_not_created_for_no_network(tmp_path: Path, capsys) -> None:
    reconstruct.main(
        [
            "--series-id",
            "DCOILWTICO",
            "--no-network",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "official_archive_network_attempted_count=0" in output
    assert "placeholder_only_archive_entry_count=0" in output
    assert not list(tmp_path.glob("*.metadata.json"))


def test_implemented_adapter_requires_artifact_and_rows(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    result = EiaWtiFetchResult(
        url="https://www.eia.gov/dnav/pet/hist/RWTCD.htm",
        status_code=200,
        content_type="text/html",
        content=b"official",
        observations=(
            EiaWtiObservation(
                observation_date="1986-01-06",
                availability_date="1986-01-07",
                value=26.53,
                unit="Dollars per Barrel",
                correction_status="official_history_candidate",
            ),
        ),
        release_date="2026-06-17",
        parse_status="parsed",
    )
    monkeypatch.setattr(reconstruct, "fetch_eia_wti_history", lambda url: result)

    reconstruct.main(
        [
            "--series-id",
            "DCOILWTICO",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "official_archive_artifact_downloaded_count=1" in output
    assert "official_archive_parse_succeeded_count=1" in output
    assert "official_archive_extracted_row_count=1" in output
    assert "implemented_archive_entry_without_artifact_count=0" in output
    assert "implemented_archive_entry_without_parsed_rows_count=0" in output
