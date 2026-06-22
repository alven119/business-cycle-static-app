from __future__ import annotations

from pathlib import Path

import scripts.reconstruct_formal_official_archives as reconstruct
from business_cycle.data_sources.census_release_index import CensusReleaseIndexItem


def test_reconstruct_cli_accepts_all_unresolved_alias(tmp_path: Path, capsys) -> None:
    reconstruct.main(
        [
            "--all-unresolved-formal",
            "--no-network",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "requested_series_count=7" in output
    assert "official_archive_source_candidate_count=11" in output
    assert "result=blocked" in output


def test_dgorder_pdf_attempt_fails_closed_on_image_only_pdf(monkeypatch) -> None:
    def fake_download(_url: str) -> tuple[int, str, bytes]:
        return 200, "application/pdf", b"%PDF-1.5\nimage-only\n%%EOF"

    monkeypatch.setattr(reconstruct, "_download_url", fake_download)
    item = CensusReleaseIndexItem(
        release_family="DGORDER",
        release_date=None,
        reference_period="1998-01",
        estimate_stage="full",
        landing_page_url="https://www.census.gov/manufacturing/m3/historical_data/index.html",
        artifact_url="https://www.census.gov/manufacturing/m3/historical_data/pressreleases/prel/1998/jan98prel.pdf",
        artifact_type="pdf",
        content_type=None,
        archive_year=1998,
        official_source=True,
        discovery_method="fixture",
        artifact_filename="jan98prel.pdf",
        reference_month_candidate="1998-01",
    )

    attempt = reconstruct._attempt_dgorder_pdf_artifacts(
        {"series_id": "DGORDER"},
        {
            "source_domain": "census.gov",
            "source_url": "https://www.census.gov/manufacturing/m3/historical_data/index.html",
            "artifact_type": "official_release_archive_candidate",
        },
        "DGORDER_census_durable_goods_advance_reports",
        [item],
    )

    assert attempt is not None
    assert attempt.network_attempted is True
    assert attempt.artifact_downloaded is True
    assert attempt.parse_attempted is True
    assert attempt.parse_succeeded is False
    assert attempt.extracted_row_count == 0
    assert attempt.error_class == "CensusPdfTextError"
    assert attempt.parse_status == "blocked_pdf_text_parser_failed"
