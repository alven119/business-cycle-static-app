"""Official Census MARTS release-date workbook helpers."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Iterable


MARTS_RELEASE_DATES_URL = "https://www.census.gov/retail/marts/www/MARTSreleasedates.xls"
PARSER_ID = "census_marts_release_calendar"
PARSER_VERSION = "1"


class CensusReleaseCalendarError(ValueError):
    """Raised when the official release calendar cannot be parsed deterministically."""


@dataclass(frozen=True)
class CensusReleaseCalendarRow:
    release_family: str
    reference_month: str
    official_release_date: str
    official_release_time: str | None
    source_workbook_id: str
    source_checksum: str
    parser_version: str = PARSER_VERSION


@dataclass(frozen=True)
class CensusReleaseCalendarParseResult:
    source_url: str
    source_workbook_id: str
    source_checksum: str
    content_type: str | None
    row_count: int
    rows: tuple[CensusReleaseCalendarRow, ...]
    parse_status: str
    parser_id: str = PARSER_ID
    parser_version: str = PARSER_VERSION


def fetch_marts_release_calendar(
    *,
    url: str = MARTS_RELEASE_DATES_URL,
) -> CensusReleaseCalendarParseResult:
    """Fetch and parse the official MARTS release-date workbook."""

    request = urllib.request.Request(url, headers={"User-Agent": "business-cycle-qa1e2/1"})
    with urllib.request.urlopen(request, timeout=30.0) as response:
        content_type = str(response.headers.get("Content-Type", "unknown"))
        content = response.read()
    return parse_marts_release_calendar(content, source_url=url, content_type=content_type)


def parse_marts_release_calendar(
    content: bytes,
    *,
    source_url: str,
    content_type: str | None = None,
) -> CensusReleaseCalendarParseResult:
    """Parse an official release calendar export.

    The live Census file is a binary BIFF XLS. This project intentionally fails
    closed when no deterministic XLS engine is available; text/CSV fixtures are
    supported for parser contract tests and future structured exports.
    """

    checksum = hashlib.sha256(content).hexdigest()
    workbook_id = "MARTSreleasedates.xls"
    if content.startswith(b"\xd0\xcf\x11\xe0"):
        raise CensusReleaseCalendarError(
            "binary_xls_requires_external_parser: install a deterministic BIFF parser "
            "or obtain an official structured sibling export; directory mtime is not a release date"
        )
    text = _decode_text(content)
    rows = tuple(
        _rows_from_records(
            _read_delimited_records(text),
            source_workbook_id=workbook_id,
            source_checksum=checksum,
        )
    )
    if not rows:
        raise CensusReleaseCalendarError("release calendar contained no parseable rows")
    return CensusReleaseCalendarParseResult(
        source_url=source_url,
        source_workbook_id=workbook_id,
        source_checksum=checksum,
        content_type=content_type,
        row_count=len(rows),
        rows=rows,
        parse_status="parsed",
    )


def summarize_required_month_coverage(
    rows: Iterable[CensusReleaseCalendarRow],
    *,
    required_reference_months: Iterable[str],
) -> dict[str, object]:
    """Summarize official calendar coverage for required reference months."""

    row_list = list(rows)
    required = sorted(set(required_reference_months))
    covered = {row.reference_month for row in row_list if row.reference_month in required}
    missing = [month for month in required if month not in covered]
    return {
        "release_calendar_row_count": len(row_list),
        "release_calendar_required_month_count": len(required),
        "release_calendar_required_month_covered_count": len(covered),
        "release_calendar_missing_required_month_count": len(missing),
        "release_calendar_missing_required_months": missing,
        "directory_mtime_used_as_release_date_count": 0,
    }


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise CensusReleaseCalendarError("release calendar is not decodable text")


def _read_delimited_records(text: str) -> list[dict[str, str]]:
    sample = text[:2048]
    dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    return [{str(key).strip(): str(value).strip() for key, value in row.items()} for row in reader]


def _rows_from_records(
    records: list[dict[str, str]],
    *,
    source_workbook_id: str,
    source_checksum: str,
) -> list[CensusReleaseCalendarRow]:
    rows: list[CensusReleaseCalendarRow] = []
    for record in records:
        reference_month = _record_value(record, ("reference_month", "Reference Month", "Month"))
        release_date = _record_value(record, ("official_release_date", "Release Date", "Date"))
        release_time = _record_value(record, ("official_release_time", "Release Time", "Time"))
        if not reference_month or not release_date:
            continue
        rows.append(
            CensusReleaseCalendarRow(
                release_family="RSAFS",
                reference_month=_normalize_reference_month(reference_month),
                official_release_date=_normalize_date(release_date),
                official_release_time=release_time or None,
                source_workbook_id=source_workbook_id,
                source_checksum=source_checksum,
            )
        )
    return rows


def _record_value(record: dict[str, str], names: tuple[str, ...]) -> str | None:
    lower = {key.lower(): value for key, value in record.items()}
    for name in names:
        value = lower.get(name.lower())
        if value:
            return value
    return None


def _normalize_reference_month(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if match:
        return f"{int(match.group(2)):04d}-{int(match.group(1)):02d}"
    raise CensusReleaseCalendarError(f"unsupported reference month format: {value}")


def _normalize_date(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if match:
        return date(int(match.group(3)), int(match.group(1)), int(match.group(2))).isoformat()
    raise CensusReleaseCalendarError(f"unsupported release date format: {value}")
