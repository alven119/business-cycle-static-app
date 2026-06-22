"""Parser for Census Advance Monthly Retail Trade release text."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from business_cycle.data_sources.census_pdf_text import extract_pdf_text_layer


PARSER_ID = "census_retail_sales_pdf_text"
PARSER_VERSION = "1"

MONTHS = {
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


class CensusRetailPdfParseError(ValueError):
    """Raised when a retail release cannot be parsed deterministically."""


@dataclass(frozen=True)
class RetailReleaseEvent:
    event_id: str
    series_id: str
    release_datetime: str
    availability_date: str
    reference_month: str
    estimate_stage: str
    value: float
    unit: str
    seasonal_adjustment: str
    source_artifact_id: str
    source_checksum: str
    parser_profile: str
    parser_version: str = PARSER_VERSION


@dataclass(frozen=True)
class RetailReleaseParseResult:
    artifact_id: str
    release_datetime: str
    release_number: str | None
    reference_month: str
    document_title: str
    source_checksum: str
    parser_profile: str
    benchmark_revision_present: bool
    benchmark_revision_effective_date: str | None
    events: tuple[RetailReleaseEvent, ...]

    @property
    def advance_estimate_count(self) -> int:
        return sum(event.estimate_stage == "advance" for event in self.events)

    @property
    def revised_estimate_count(self) -> int:
        return sum(event.estimate_stage == "revised" for event in self.events)


def parse_retail_sales_release_artifact(
    content: bytes,
    *,
    artifact_id: str,
    artifact_filename: str | None = None,
) -> RetailReleaseParseResult:
    """Parse one official Census retail sales release artifact."""

    text = extract_pdf_text_layer(content)
    checksum = hashlib.sha256(content).hexdigest()
    return parse_retail_sales_release_text(
        text,
        artifact_id=artifact_id,
        source_checksum=checksum,
        artifact_filename=artifact_filename,
    )


def parse_retail_sales_release_text(
    text: str,
    *,
    artifact_id: str,
    source_checksum: str,
    artifact_filename: str | None = None,
) -> RetailReleaseParseResult:
    """Parse normalized text from one Census retail release."""

    normalized = _normalize(text)
    release_dt = _extract_release_datetime(normalized)
    reference_month = _extract_reference_month(normalized)
    filename_candidate = _filename_reference_month(artifact_filename or "")
    if filename_candidate and filename_candidate != reference_month:
        raise CensusRetailPdfParseError(
            f"filename reference month {filename_candidate} does not match body {reference_month}"
        )
    if date.fromisoformat(reference_month + "-01").replace(day=28) >= release_dt.date():
        raise CensusRetailPdfParseError("release date is not after reference month start")
    profile = _parser_profile(release_dt.date())
    release_number = _optional_match(normalized, r"\b(?:CB|FTD)-?\d{2}-\d+\b")
    title = _extract_title(normalized)
    advance_value = _extract_value(
        normalized,
        [
            r"advance\s+(?:estimate\s+)?(?:of\s+)?(?:u\.s\.\s+)?retail.*?sales.*?\$?([0-9][0-9,]+(?:\.\d+)?)\s*(?:million|billion)?",
            r"retail\s+and\s+food\s+services\s+sales.*?\$?([0-9][0-9,]+(?:\.\d+)?)\s*(?:million|billion)?",
        ],
    )
    previous_month = _shift_month(reference_month, -1)
    revised_value = _extract_value(
        normalized,
        [
            r"(?:revised|previous\s+month).*?(?:retail|sales).*?\$?([0-9][0-9,]+(?:\.\d+)?)\s*(?:million|billion)?",
            r"([0-9][0-9,]+(?:\.\d+)?)\s+revised",
        ],
        required=False,
    )
    events = [
        _event(
            artifact_id=artifact_id,
            checksum=source_checksum,
            release_dt=release_dt,
            reference_month=reference_month,
            stage="advance",
            value=advance_value,
            profile=profile,
        )
    ]
    if revised_value is not None:
        events.append(
            _event(
                artifact_id=artifact_id,
                checksum=source_checksum,
                release_dt=release_dt,
                reference_month=previous_month,
                stage="revised",
                value=revised_value,
                profile=profile,
            )
        )
    benchmark = "benchmark" in normalized.lower()
    return RetailReleaseParseResult(
        artifact_id=artifact_id,
        release_datetime=release_dt.isoformat(),
        release_number=release_number,
        reference_month=reference_month,
        document_title=title,
        source_checksum=source_checksum,
        parser_profile=profile,
        benchmark_revision_present=benchmark,
        benchmark_revision_effective_date=release_dt.date().isoformat() if benchmark else None,
        events=tuple(events),
    )


def _event(
    *,
    artifact_id: str,
    checksum: str,
    release_dt: datetime,
    reference_month: str,
    stage: str,
    value: float,
    profile: str,
) -> RetailReleaseEvent:
    return RetailReleaseEvent(
        event_id=f"RSAFS|{reference_month}|{stage}|{release_dt.date().isoformat()}|{artifact_id}",
        series_id="RSAFS",
        release_datetime=release_dt.isoformat(),
        availability_date=release_dt.date().isoformat(),
        reference_month=reference_month,
        estimate_stage=stage,
        value=value,
        unit="millions_of_dollars",
        seasonal_adjustment="seasonally_adjusted",
        source_artifact_id=artifact_id,
        source_checksum=checksum,
        parser_profile=profile,
    )


def _extract_release_datetime(text: str) -> datetime:
    patterns = [
        r"FOR RELEASE AT\s+[0-9:]+\s*A\.?M\.?\s+\w+\s*,?\s+([A-Za-z]+)\s+(\d{1,2}),\s+((?:19|20)\d{2})",
        r"Released?\s+(?:on\s+)?([A-Za-z]+)\s+(\d{1,2}),\s+((?:19|20)\d{2})",
        r"([A-Za-z]+)\s+(\d{1,2}),\s+((?:19|20)\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            month = MONTHS[match.group(1).lower()]
            return datetime(int(match.group(3)), month, int(match.group(2)), 8, 30)
    raise CensusRetailPdfParseError("release datetime not found in text layer")


def _extract_reference_month(text: str) -> str:
    patterns = [
        r"advance\s+(?:monthly\s+)?(?:retail.*?sales).*?\bfor\s+([A-Za-z]+)\s+((?:19|20)\d{2})",
        r"\b([A-Za-z]+)\s+((?:19|20)\d{2})\s+(?:advance\s+)?retail",
        r"\b([A-Za-z]+)\s+((?:19|20)\d{2})\s+sales",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match and match.group(1).lower() in MONTHS:
            return f"{int(match.group(2)):04d}-{MONTHS[match.group(1).lower()]:02d}"
    raise CensusRetailPdfParseError("reference month not found in text layer")


def _extract_value(text: str, patterns: list[str], *, required: bool = True) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return float(match.group(1).replace(",", ""))
    if required:
        raise CensusRetailPdfParseError("required retail estimate value not found")
    return None


def _extract_title(text: str) -> str:
    for line in text.splitlines():
        if "retail" in line.lower() and "sales" in line.lower():
            return line.strip()
    return "Advance Monthly Retail Trade Survey"


def _optional_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.I)
    return match.group(0) if match else None


def _parser_profile(release_date: date) -> str:
    if release_date.year <= 2008:
        return "legacy_2000_2008"
    if release_date.year <= 2016:
        return "transitional_2009_2016"
    return "modern_2017_present"


def _filename_reference_month(filename: str) -> str | None:
    match = re.search(r"adv(\d{2})(\d{2})", Path(filename).name.lower())
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2))
    if not 1 <= month <= 12:
        return None
    return f"{2000 + year if year < 70 else 1900 + year:04d}-{month:02d}"


def _shift_month(reference_month: str, offset: int) -> str:
    year, month = (int(part) for part in reference_month.split("-"))
    month += offset
    while month < 1:
        year -= 1
        month += 12
    while month > 12:
        year += 1
        month -= 12
    return f"{year:04d}-{month:02d}"


def _normalize(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())
