from __future__ import annotations

from pathlib import Path

import business_cycle.data_sources.controlled_official_pdf_ocr as ocr


def test_controlled_ocr_dual_disagreement_fails_closed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf = tmp_path / "adv9801.pdf"
    pdf.write_bytes(b"%PDF-fixture")
    calls: list[tuple[int, int]] = []

    def fake_extract(_path: Path, *, dpi: int, psm: int) -> ocr.OcrExtraction:
        calls.append((dpi, psm))
        value = 214760 if dpi == 300 else 214761
        return ocr.OcrExtraction(
            release_date="1998-02-12",
            reference_month="1998-01",
            headline_value_millions=214800,
            table_value_millions=value,
            unit="millions_of_dollars",
            seasonal_adjustment="seasonally_adjusted",
        )

    monkeypatch.setattr(ocr, "_extract_rsafs", fake_extract)

    result = ocr.verify_rsafs_pdf_ocr(
        pdf,
        artifact_id="fixture",
        expected_release_date="1998-02-12",
        expected_reference_month="1998-01",
    )

    assert calls == [(300, 4), (400, 6)]
    assert result.verified is False
    assert result.evidence_class == "official_release_archive_ocr_rejected"
    assert result.rejected_reason == "dual_numeric_disagreement"


def test_controlled_ocr_cross_release_required_even_when_dual_values_match(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf = tmp_path / "adv9801.pdf"
    pdf.write_bytes(b"%PDF-fixture")

    def fake_extract(_path: Path, *, dpi: int, psm: int) -> ocr.OcrExtraction:
        return ocr.OcrExtraction(
            release_date="1998-02-12",
            reference_month="1998-01",
            headline_value_millions=214800,
            table_value_millions=214760,
            unit="millions_of_dollars",
            seasonal_adjustment="seasonally_adjusted",
        )

    monkeypatch.setattr(ocr, "_extract_rsafs", fake_extract)

    result = ocr.verify_rsafs_pdf_ocr(
        pdf,
        artifact_id="fixture",
        expected_release_date="1998-02-12",
        expected_reference_month="1998-01",
    )

    assert result.dual_numeric_agreement is True
    assert result.cross_release_validation_pass is False
    assert result.verified is False
    assert result.rejected_reason == "cross_release_validation_failed"
