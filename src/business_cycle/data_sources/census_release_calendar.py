"""Official Census MARTS release-date workbook helpers."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from business_cycle.data_sources.legacy_xls import (
    PARSER_ID as LEGACY_XLS_PARSER_ID,
    PARSER_VERSION as LEGACY_XLS_PARSER_VERSION,
    LegacyXlsError,
    open_legacy_workbook,
)


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
    workbook_artifact_id: str
    workbook_checksum: str
    workbook_sheet_name: str
    source_row_number: int
    parser_id: str = PARSER_ID
    parser_version: str = PARSER_VERSION

    @property
    def source_workbook_id(self) -> str:
        """Backward-compatible workbook ID alias."""

        return self.workbook_artifact_id

    @property
    def source_checksum(self) -> str:
        """Backward-compatible checksum alias."""

        return self.workbook_checksum


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


@dataclass(frozen=True)
class CensusReleaseCalendarSummary:
    release_calendar_artifact_count: int
    release_calendar_sheet_count: int
    release_calendar_row_count: int
    required_reference_month_count: int
    required_reference_month_covered_count: int
    required_reference_month_missing_count: int
    duplicate_reference_month_count: int
    invalid_release_date_count: int
    directory_mtime_used_as_release_date_count: int


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


def parse_marts_release_calendar_workbook(path: str | Path) -> CensusReleaseCalendarParseResult:
    """Parse the official MARTS release-date BIFF workbook from disk."""

    workbook = open_legacy_workbook(path)
    sheet = workbook.book.sheet_by_index(0)
    rows: list[CensusReleaseCalendarRow] = []
    duplicates: set[str] = set()
    seen: set[str] = set()
    invalid_dates = 0
    headers = [str(sheet.cell_value(3, col)).strip() for col in range(sheet.ncols)]
    month_columns = [
        (col, _month_number(name))
        for col, name in enumerate(headers)
        if _month_number(name) is not None
    ]
    if not month_columns:
        raise CensusReleaseCalendarError("required month columns not found")
    for row_index in range(4, sheet.nrows):
        year_value = sheet.cell_value(row_index, 0)
        if not isinstance(year_value, float):
            continue
        year = int(year_value)
        for col, month in month_columns:
            day_value = sheet.cell_value(row_index, col)
            if day_value in ("", None):
                continue
            release_day = _release_day_from_cell(day_value)
            if release_day is None:
                continue
            try:
                reference_year, reference_month = _reference_month_for_lagged_release(
                    release_year=year,
                    release_month=month,
                )
                release_date = date(year, month, release_day)
            except (TypeError, ValueError):
                invalid_dates += 1
                continue
            if release_date <= date(reference_year, reference_month, 1):
                invalid_dates += 1
                continue
            reference = f"{reference_year:04d}-{reference_month:02d}"
            if reference in seen:
                duplicates.add(reference)
                continue
            seen.add(reference)
            rows.append(
                CensusReleaseCalendarRow(
                    release_family="RSAFS",
                    reference_month=reference,
                    official_release_date=release_date.isoformat(),
                    official_release_time="08:30",
                    workbook_artifact_id=Path(path).name,
                    workbook_checksum=workbook.checksum,
                    workbook_sheet_name=sheet.name,
                    source_row_number=row_index + 1,
                    parser_id=f"{PARSER_ID}+{LEGACY_XLS_PARSER_ID}",
                    parser_version=f"{PARSER_VERSION}.{LEGACY_XLS_PARSER_VERSION}",
                )
            )
    if invalid_dates:
        raise CensusReleaseCalendarError(f"invalid release date cells detected: {invalid_dates}")
    if duplicates:
        raise CensusReleaseCalendarError(
            "duplicate reference months detected: " + ",".join(sorted(duplicates))
        )
    if not rows:
        raise CensusReleaseCalendarError("release calendar contained no parseable BIFF rows")
    return CensusReleaseCalendarParseResult(
        source_url=MARTS_RELEASE_DATES_URL,
        source_workbook_id=Path(path).name,
        source_checksum=workbook.checksum,
        content_type="application/vnd.ms-excel",
        row_count=len(rows),
        rows=tuple(rows),
        parse_status="parsed",
    )


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
        tmp_path = Path("/tmp") / "MARTSreleasedates.xls"
        tmp_path.write_bytes(content)
        try:
            return parse_marts_release_calendar_workbook(tmp_path)
        except LegacyXlsError as exc:
            raise CensusReleaseCalendarError(str(exc)) from exc
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
                workbook_artifact_id=source_workbook_id,
                workbook_checksum=source_checksum,
                workbook_sheet_name="structured_export",
                source_row_number=len(rows) + 1,
            )
        )
    return rows


def summarize_release_calendar(
    rows: Iterable[CensusReleaseCalendarRow],
    *,
    required_reference_months: Iterable[str],
) -> CensusReleaseCalendarSummary:
    """Return QA summary for release-calendar parsing."""

    row_list = list(rows)
    required = sorted(set(required_reference_months))
    covered = {row.reference_month for row in row_list if row.reference_month in required}
    duplicates = len(row_list) - len({row.reference_month for row in row_list})
    return CensusReleaseCalendarSummary(
        release_calendar_artifact_count=1 if row_list else 0,
        release_calendar_sheet_count=len({row.workbook_sheet_name for row in row_list}),
        release_calendar_row_count=len(row_list),
        required_reference_month_count=len(required),
        required_reference_month_covered_count=len(covered),
        required_reference_month_missing_count=len(required) - len(covered),
        duplicate_reference_month_count=duplicates,
        invalid_release_date_count=0,
        directory_mtime_used_as_release_date_count=0,
    )


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


def _month_number(name: str) -> int | None:
    months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    return months.get(name.strip().lower()[:3])


def _release_day_from_cell(value: object) -> int | None:
    if value in ("", None):
        return None
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if text.upper() in {"N/A", "TBA"}:
        return None
    if "," in text:
        return None
    match = re.fullmatch(r"(\d{1,2})(?:\*\*)?", text)
    if match:
        return int(match.group(1))
    raise ValueError(f"unsupported release date cell: {text}")


def _reference_month_for_lagged_release(
    *,
    release_year: int,
    release_month: int,
) -> tuple[int, int]:
    reference_month = release_month - 1
    reference_year = release_year
    if reference_month == 0:
        reference_month = 12
        reference_year -= 1
    return reference_year, reference_month
