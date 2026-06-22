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


@dataclass(frozen=True)
class CensusReleaseIndexSummary:
    census_release_index_page_count: int
    census_release_link_count: int
    census_direct_artifact_link_count: int
    census_landing_page_only_count: int
    census_duplicate_release_link_count: int
    census_release_without_date_count: int


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
        items.append(
            CensusReleaseIndexItem(
                release_family=release_family,
                release_date=None,
                reference_period=period,
                estimate_stage=_estimate_stage(release_family),
                landing_page_url=landing_page_url,
                artifact_url=url,
                artifact_type=artifact_type,
                content_type=content_type if not is_direct else None,
                archive_year=int(period[:4]) if period else None,
                official_source=True,
                discovery_method="census_release_index_link",
                checksum_if_downloaded=checksum if url == landing_page_url else None,
            )
        )
    summary = CensusReleaseIndexSummary(
        census_release_index_page_count=1,
        census_release_link_count=len(items),
        census_direct_artifact_link_count=sum(item.artifact_type != "html_landing_page" for item in items),
        census_landing_page_only_count=sum(item.artifact_type == "html_landing_page" for item in items),
        census_duplicate_release_link_count=duplicate_count,
        census_release_without_date_count=sum(item.release_date is None for item in items),
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
