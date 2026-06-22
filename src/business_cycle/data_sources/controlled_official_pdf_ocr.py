"""Controlled OCR for official image-only Census PDFs."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


PARSER_ID = "controlled_official_pdf_ocr"
PARSER_VERSION = "1"


class ControlledOcrError(ValueError):
    """Raised when OCR cannot be executed or validated."""


@dataclass(frozen=True)
class OcrExtraction:
    release_date: str | None
    reference_month: str | None
    headline_value_millions: int | None
    table_value_millions: int | None
    unit: str | None
    seasonal_adjustment: str | None


@dataclass(frozen=True)
class ControlledOcrResult:
    artifact_id: str
    artifact_checksum: str
    evidence_class: str
    extraction_method: str
    parser_id: str
    parser_version: str
    run_a: OcrExtraction
    run_b: OcrExtraction
    release_date_match: bool
    reference_month_match: bool
    dual_numeric_agreement: bool
    headline_table_match: bool
    arithmetic_validation_pass: bool
    cross_release_validation_pass: bool
    verified: bool
    rejected_reason: str | None


def verify_rsafs_pdf_ocr(
    pdf_path: str | Path,
    *,
    artifact_id: str,
    expected_release_date: str,
    expected_reference_month: str,
) -> ControlledOcrResult:
    """Run dual OCR on an RSAFS release PDF and fail closed unless fully verified."""

    path = Path(pdf_path)
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    run_a = _extract_rsafs(path, dpi=300, psm=4)
    run_b = _extract_rsafs(path, dpi=400, psm=6)
    release_date_match = (
        run_a.release_date == run_b.release_date == expected_release_date
    )
    reference_month_match = (
        run_a.reference_month == run_b.reference_month == expected_reference_month
    )
    dual_numeric_agreement = (
        run_a.table_value_millions is not None
        and run_a.table_value_millions == run_b.table_value_millions
    )
    headline_table_match = (
        run_a.headline_value_millions is not None
        and run_a.table_value_millions is not None
        and abs(run_a.headline_value_millions - run_a.table_value_millions) <= 100
        and run_b.headline_value_millions is not None
        and run_b.table_value_millions is not None
        and abs(run_b.headline_value_millions - run_b.table_value_millions) <= 100
    )
    arithmetic_validation_pass = headline_table_match
    cross_release_validation_pass = False
    rejected_reason = _rejected_reason(
        release_date_match=release_date_match,
        reference_month_match=reference_month_match,
        dual_numeric_agreement=dual_numeric_agreement,
        headline_table_match=headline_table_match,
        arithmetic_validation_pass=arithmetic_validation_pass,
        cross_release_validation_pass=cross_release_validation_pass,
    )
    verified = rejected_reason is None
    return ControlledOcrResult(
        artifact_id=artifact_id,
        artifact_checksum=checksum,
        evidence_class=(
            "official_release_archive_ocr_verified"
            if verified
            else "official_release_archive_ocr_rejected"
        ),
        extraction_method="pdf_ocr_verified" if verified else "pdf_ocr_rejected",
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        run_a=run_a,
        run_b=run_b,
        release_date_match=release_date_match,
        reference_month_match=reference_month_match,
        dual_numeric_agreement=dual_numeric_agreement,
        headline_table_match=headline_table_match,
        arithmetic_validation_pass=arithmetic_validation_pass,
        cross_release_validation_pass=cross_release_validation_pass,
        verified=verified,
        rejected_reason=rejected_reason,
    )


def _extract_rsafs(path: Path, *, dpi: int, psm: int) -> OcrExtraction:
    texts: list[str] = []
    for page in (1, 2):
        image = convert_from_path(str(path), dpi=dpi, first_page=page, last_page=page, fmt="png")[0]
        texts.append(pytesseract.image_to_string(image, lang="eng", config=f"--psm {psm}"))
    text = "\n".join(texts)
    return OcrExtraction(
        release_date=_extract_release_date(text),
        reference_month=_extract_reference_month(text),
        headline_value_millions=_extract_headline_value(text),
        table_value_millions=_extract_table_value(text),
        unit="millions_of_dollars" if "Millions of Dollars" in text else None,
        seasonal_adjustment=(
            "seasonally_adjusted"
            if "adjusted for seasonal" in text.lower() or "Adjusted" in text
            else None
        ),
    )


def _extract_release_date(text: str) -> str | None:
    match = re.search(
        r"FOR\s+(?:WIRE\s+)?TRANSMI\w*\s+8:30\s*A\.?M\.?.*?,\s*"
        r"([A-Za-z]+)\s+(\d{1,2}),\s+((?:19|20)\d{2})",
        text,
        re.I,
    )
    if not match:
        return None
    return date(int(match.group(3)), _month_number(match.group(1)), int(match.group(2))).isoformat()


def _extract_reference_month(text: str) -> str | None:
    match = re.search(r"ADVANCE MONTHLY RETAIL SALES\s+([A-Z]+)\s+((?:19|20)\d{2})", text, re.I)
    if not match:
        return None
    return f"{int(match.group(2)):04d}-{_month_number(match.group(1)):02d}"


def _extract_headline_value(text: str) -> int | None:
    match = re.search(r"were\s+\$([0-9]+(?:\.[0-9]+)?)\s+billion", text, re.I)
    if not match:
        return None
    return int(round(float(match.group(1)) * 1000))


def _extract_table_value(text: str) -> int | None:
    match = re.search(r"Retail trade, total.*", text, re.I)
    if not match:
        return None
    numbers = [int(item.replace(",", "")) for item in re.findall(r"\d{1,3}(?:,\d{3})+", match.group(0))]
    if len(numbers) < 10:
        return None
    return numbers[5]


def _rejected_reason(
    *,
    release_date_match: bool,
    reference_month_match: bool,
    dual_numeric_agreement: bool,
    headline_table_match: bool,
    arithmetic_validation_pass: bool,
    cross_release_validation_pass: bool,
) -> str | None:
    checks = {
        "release_date_mismatch": release_date_match,
        "reference_month_mismatch": reference_month_match,
        "dual_numeric_disagreement": dual_numeric_agreement,
        "headline_table_mismatch": headline_table_match,
        "arithmetic_validation_failed": arithmetic_validation_pass,
        "cross_release_validation_failed": cross_release_validation_pass,
    }
    for reason, passed in checks.items():
        if not passed:
            return reason
    return None


def _month_number(name: str) -> int:
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    key = name.lower()
    if key not in months:
        raise ControlledOcrError(f"unsupported month name: {name}")
    return months[key]
