"""EIA WTI official observational archive adapter."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html import unescape
from typing import Callable


EIA_WTI_HISTORY_URL = "https://www.eia.gov/dnav/pet/hist/RWTCD.htm"
PARSER_ID = "eia_wti_observational_archive"
PARSER_VERSION = "1"


class EiaWtiArchiveError(ValueError):
    """Raised when EIA WTI archive content cannot be fetched or parsed."""


@dataclass(frozen=True)
class EiaWtiObservation:
    """One parsed WTI daily observation from the EIA history artifact."""

    observation_date: str
    availability_date: str
    value: float
    unit: str
    correction_status: str
    parser_version: str = PARSER_VERSION


@dataclass(frozen=True)
class EiaWtiFetchResult:
    """Downloaded EIA artifact plus parser diagnostics."""

    url: str
    status_code: int
    content_type: str
    content: bytes
    observations: tuple[EiaWtiObservation, ...]
    release_date: str | None
    parse_status: str


def fetch_eia_wti_history(
    *,
    url: str = EIA_WTI_HISTORY_URL,
    timeout_seconds: float = 30.0,
    opener: Callable[[str, float], tuple[int, str, bytes]] | None = None,
) -> EiaWtiFetchResult:
    """Download and parse the official EIA WTI history page."""

    status_code, content_type, content = (opener or _download)(url, timeout_seconds)
    observations, release_date = parse_eia_wti_history_html(content)
    return EiaWtiFetchResult(
        url=url,
        status_code=status_code,
        content_type=content_type,
        content=content,
        observations=tuple(observations),
        release_date=release_date,
        parse_status="parsed" if observations else "parsed_zero_rows",
    )


def parse_eia_wti_history_html(content: bytes | str) -> tuple[list[EiaWtiObservation], str | None]:
    """Parse WTI daily rows from the EIA history HTML text table.

    The EIA dnav history page exposes daily WTI values as an official HTML artifact.
    This parser intentionally treats the values as an observational archive candidate:
    it extracts dated observations and uses a conservative next-day availability rule
    for diagnostics, but it does not by itself prove strict historical release semantics.
    """

    text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"\s+", " ", text)
    release_date = _parse_release_date(text)
    observations: list[EiaWtiObservation] = []
    seen: set[str] = set()
    for match in _WEEK_ROW_RE.finditer(text):
        year = int(match.group("year"))
        start_month = _MONTHS[match.group("start_month")]
        start_day = int(match.group("start_day"))
        end_month_name = match.group("end_month") or match.group("start_month")
        end_month = _MONTHS[end_month_name]
        values = [float(item) for item in _VALUE_RE.findall(match.group("values"))]
        if not values:
            continue
        start_year = year
        end_year = year + 1 if end_month < start_month else year
        try:
            current = date(start_year, start_month, start_day)
            end = date(end_year, end_month, int(match.group("end_day")))
        except ValueError:
            continue
        business_dates = _business_dates(current, end)
        for observation_date, value in zip(business_dates, values, strict=False):
            obs_date = observation_date.isoformat()
            if obs_date in seen:
                continue
            seen.add(obs_date)
            observations.append(
                EiaWtiObservation(
                    observation_date=obs_date,
                    availability_date=(observation_date + timedelta(days=1)).isoformat(),
                    value=value,
                    unit="Dollars per Barrel",
                    correction_status="official_history_candidate",
                )
            )
    return sorted(observations, key=lambda item: item.observation_date), release_date


def _download(url: str, timeout_seconds: float) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "business-cycle-qa1d/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", 200))
            content_type = str(response.headers.get("Content-Type", "unknown"))
            content = response.read()
    except urllib.error.URLError as exc:
        raise EiaWtiArchiveError(f"EIA WTI download failed: {type(exc).__name__}") from exc
    if status >= 400:
        raise EiaWtiArchiveError(f"EIA WTI download failed with http_status={status}")
    return status, content_type, content


def _business_dates(start: date, end: date) -> list[date]:
    dates: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def _parse_release_date(text: str) -> str | None:
    match = re.search(r"Release Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})", text)
    if not match:
        return None
    value = match.group(1)
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


_MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}
_VALUE_RE = re.compile(r"\b\d+\.\d+\b")
_WEEK_ROW_RE = re.compile(
    r"(?P<year>\d{4})\s+"
    r"(?P<start_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\s*"
    r"(?P<start_day>\d{1,2})\s+to\s+"
    r"(?:(?P<end_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\s*)?"
    r"(?P<end_day>\d{1,2})\s+"
    r"(?P<values>(?:\d+\.\d+\s+){1,5})",
)
