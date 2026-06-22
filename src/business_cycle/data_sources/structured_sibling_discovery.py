"""Probe official structured siblings for Census PDF release artifacts."""

from __future__ import annotations

import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable


STRUCTURED_SUFFIXES = (".xls", ".xlsx", ".csv", ".txt", ".html", ".xml", ".json")
HEAD_TIMEOUT_SECONDS = 3.0


@dataclass(frozen=True)
class StructuredSiblingProbeResult:
    required_release_count: int
    structured_sibling_probe_count: int
    structured_sibling_found_count: int
    xls_found_count: int
    xlsx_found_count: int
    csv_found_count: int
    txt_found_count: int
    html_data_table_found_count: int
    image_pdf_only_count: int
    unresolved_artifact_count: int
    found_urls: tuple[str, ...]


def probe_structured_siblings(
    pdf_urls: list[str],
    *,
    exists: Callable[[str], bool] | None = None,
) -> StructuredSiblingProbeResult:
    """Probe official same-basename structured sibling URLs for each PDF URL."""

    exists_fn = exists or _head_exists
    found: list[str] = []
    probe_count = 0
    image_only = 0
    for pdf_url in pdf_urls:
        release_found = False
        for candidate_url in _candidate_urls(pdf_url):
            probe_count += 1
            if exists_fn(candidate_url):
                found.append(candidate_url)
                release_found = True
                break
        if not release_found:
            image_only += 1
    suffix_counts = {suffix: 0 for suffix in STRUCTURED_SUFFIXES}
    for url in found:
        suffix = "." + urllib.parse.urlparse(url).path.rsplit(".", 1)[-1].lower()
        if suffix in suffix_counts:
            suffix_counts[suffix] += 1
    return StructuredSiblingProbeResult(
        required_release_count=len(pdf_urls),
        structured_sibling_probe_count=probe_count,
        structured_sibling_found_count=len(found),
        xls_found_count=suffix_counts[".xls"],
        xlsx_found_count=suffix_counts[".xlsx"],
        csv_found_count=suffix_counts[".csv"],
        txt_found_count=suffix_counts[".txt"],
        html_data_table_found_count=suffix_counts[".html"],
        image_pdf_only_count=image_only,
        unresolved_artifact_count=image_only,
        found_urls=tuple(found),
    )


def _candidate_urls(pdf_url: str) -> list[str]:
    parsed = urllib.parse.urlparse(pdf_url)
    base = parsed.path.rsplit(".", 1)[0]
    return [
        urllib.parse.urlunparse(parsed._replace(path=base + suffix))
        for suffix in STRUCTURED_SUFFIXES
    ]


def _head_exists(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    if not (host.endswith("census.gov") or host.endswith("www2.census.gov")):
        return False
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "business-cycle-qa1e2/1"})
    try:
        with urllib.request.urlopen(request, timeout=HEAD_TIMEOUT_SECONDS) as response:
            return int(getattr(response, "status", 200)) < 400
    except Exception:  # noqa: BLE001 - a missing sibling is a negative probe.
        return False
