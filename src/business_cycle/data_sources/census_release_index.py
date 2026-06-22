"""Official Census release index discovery helpers."""

from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable


MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
}


@dataclass(frozen=True)
class CensusReleaseIndexItem:
    release_family: str
    release_date: str | None
    reference_period: str | None
    estimate_stage: str
    landing_page_url: str
    artifact_url: str
    artifact_type: str
    content_type: str | None
    archive_year: int | None
    official_source: bool
    discovery_method: str
    checksum_if_downloaded: str | None = None
    artifact_filename: str | None = None
    reference_month_candidate: str | None = None
    verified_reference_month: str | None = None
    release_datetime: str | None = None
    release_date_source: str | None = None
    release_date_confidence: str = "unresolved"
    http_last_modified: str | None = None
    directory_last_modified: str | None = None
    last_modified_used_as_release_date: bool = False
    verification_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class CensusReleaseIndexSummary:
    census_release_index_page_count: int
    census_release_link_count: int
    census_direct_artifact_link_count: int
    census_landing_page_only_count: int
    census_duplicate_release_link_count: int
    census_release_without_date_count: int
    pdf_text_release_date_count: int = 0
    official_calendar_release_date_count: int = 0
    unresolved_release_date_count: int = 0
    directory_mtime_rejected_count: int = 0
    filename_reference_month_match_count: int = 0
    filename_reference_month_mismatch_count: int = 0


def fetch_census_release_index(
    *,
    release_family: str,
    landing_page_url: str,
    opener: Callable[[str], tuple[str | None, bytes]] | None = None,
) -> tuple[list[CensusReleaseIndexItem], CensusReleaseIndexSummary]:
    """Fetch and parse one official Census release index page."""

    content_type, content = (opener or _download)(landing_page_url)
    return parse_census_release_index(
        release_family=release_family,
        landing_page_url=landing_page_url,
        html=content,
        content_type=content_type,
        checksum=hashlib.sha256(content).hexdigest(),
    )


def parse_census_release_index(
    *,
    release_family: str,
    landing_page_url: str,
    html: bytes | str,
    content_type: str | None = None,
    checksum: str | None = None,
) -> tuple[list[CensusReleaseIndexItem], CensusReleaseIndexSummary]:
    """Parse official Census release links from a landing page."""

    text = html.decode("utf-8", errors="ignore") if isinstance(html, bytes) else html
    parser = _LinkParser()
    parser.feed(text)
    items: list[CensusReleaseIndexItem] = []
    seen_urls: set[str] = set()
    duplicate_count = 0
    for href, label in parser.links:
        url = urllib.parse.urljoin(landing_page_url, href)
        if not _is_official_census_url(url):
            continue
        artifact_type = _artifact_type(url)
        is_direct = artifact_type != "html_landing_page"
        if url in seen_urls:
            duplicate_count += 1
            continue
        seen_urls.add(url)
        period = _month_year(label)
        filename_period = _filename_reference_month_candidate(url)
        reference_period = period or filename_period
        items.append(
            CensusReleaseIndexItem(
                release_family=release_family,
                release_date=None,
                reference_period=reference_period,
                estimate_stage=_estimate_stage(release_family),
                landing_page_url=landing_page_url,
                artifact_url=url,
                artifact_type=artifact_type,
                content_type=content_type if not is_direct else None,
                archive_year=int(reference_period[:4]) if reference_period else None,
                official_source=True,
                discovery_method="census_release_index_link",
                checksum_if_downloaded=checksum if url == landing_page_url else None,
                artifact_filename=_artifact_filename(url),
                reference_month_candidate=filename_period,
                release_date_confidence="unresolved",
                verification_warnings=(
                    ("filename_reference_month_candidate_unverified",)
                    if filename_period and filename_period != period
                    else ()
                ),
            )
        )
    summary = CensusReleaseIndexSummary(
        census_release_index_page_count=1,
        census_release_link_count=len(items),
        census_direct_artifact_link_count=sum(item.artifact_type != "html_landing_page" for item in items),
        census_landing_page_only_count=sum(item.artifact_type == "html_landing_page" for item in items),
        census_duplicate_release_link_count=duplicate_count,
        census_release_without_date_count=sum(item.release_date is None for item in items),
        unresolved_release_date_count=sum(item.release_date is None for item in items),
        directory_mtime_rejected_count=sum(item.artifact_type != "html_landing_page" for item in items),
        filename_reference_month_match_count=sum(
            item.reference_period is not None
            and item.reference_month_candidate == item.reference_period
            for item in items
        ),
        filename_reference_month_mismatch_count=sum(
            item.reference_month_candidate is not None
            and item.reference_period is not None
            and item.reference_month_candidate != item.reference_period
            for item in items
        ),
    )
    return items, summary


def _download(url: str) -> tuple[str | None, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "business-cycle-qa1e1/1"})
    with urllib.request.urlopen(request, timeout=30.0) as response:
        return str(response.headers.get("Content-Type", "unknown")), response.read()


def _is_official_census_url(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return host.endswith("census.gov")


def _artifact_type(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    if path.endswith(".csv"):
        return "csv"
    if path.endswith((".xls", ".xlsx")):
        return "xls"
    if path.endswith(".json"):
        return "json"
    if path.endswith(".xml"):
        return "xml"
    if path.endswith(".txt"):
        return "txt"
    if path.endswith(".pdf"):
        return "pdf"
    return "html_landing_page"


def _artifact_filename(url: str) -> str:
    """Return the final URL path component without treating it as provenance."""

    return urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]


def _month_year(label: str) -> str | None:
    match = re.search(
        r"\b("
        + "|".join(MONTHS)
        + r")\s+((?:19|20)\d{2})\b",
        label,
    )
    if not match:
        return None
    return f"{match.group(2)}-{MONTHS[match.group(1)]}"


def _filename_reference_month_candidate(url: str) -> str | None:
    filename = _artifact_filename(url).lower()
    match = re.search(r"(?:adv|marts|m3|dg)?(\d{2})(\d{2})", filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        if not 1 <= month <= 12:
            return None
        full_year = 2000 + year if year < 70 else 1900 + year
        return f"{full_year:04d}-{month:02d}"
    month_names = {
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
    match = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{2})", filename)
    if not match:
        return None
    year = int(match.group(2))
    month = month_names[match.group(1)]
    if not 1 <= month <= 12:
        return None
    full_year = 2000 + year if year < 70 else 1900 + year
    return f"{full_year:04d}-{month:02d}"


def _estimate_stage(release_family: str) -> str:
    if release_family.lower() == "rsafs":
        return "advance"
    if release_family.lower() == "dgorder":
        return "full"
    return "unknown"


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href:
            label = " ".join(part.strip() for part in self._current_text if part.strip())
            self.links.append((self._current_href, label))
            self._current_href = None
            self._current_text = []
