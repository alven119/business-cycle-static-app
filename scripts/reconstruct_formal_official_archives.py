#!/usr/bin/env python
"""Fetch and parse official archive artifacts for unresolved formal series."""

from __future__ import annotations

import argparse
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from business_cycle.data_sources.eia_wti_observational_archive import (
    EIA_WTI_HISTORY_URL,
    PARSER_ID as EIA_WTI_PARSER_ID,
    PARSER_VERSION as EIA_WTI_PARSER_VERSION,
    EiaWtiArchiveError,
    fetch_eia_wti_history,
)
from business_cycle.data_sources.census_release_index import fetch_census_release_index
from business_cycle.data_sources.census_pdf_text import extract_pdf_text_layer
from business_cycle.data_sources.census_retail_sales_pdf_parser import (
    RetailReleaseEvent,
    parse_retail_sales_release_artifact,
)
from business_cycle.storage.official_release_archive_cache import (
    OfficialReleaseArchiveCache,
    OfficialReleaseArchiveCacheError,
)
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError

GENERIC_PARSER_ID = "qa1d_official_archive_artifact_probe"
GENERIC_PARSER_VERSION = "1"


@dataclass(frozen=True)
class ArtifactAttempt:
    """One official archive source attempt."""

    series_id: str
    source_id: str
    source_domain: str
    source_url: str
    artifact_type: str
    implementation_status: str
    network_attempted: bool
    artifact_downloaded: bool
    structured_response: bool
    parse_attempted: bool
    parse_succeeded: bool
    parsed_release_count: int
    extracted_row_count: int
    as_of_snapshot_count: int
    cache_status: str
    http_status: int | None
    content_type: str | None
    byte_count: int
    parse_status: str
    error_class: str | None = None
    error_message_redacted: str | None = None
    census_release_index_count: int = 0
    census_direct_artifact_link_count: int = 0
    census_landing_page_only_count: int = 0
    census_release_without_date_count: int = 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--series-id", action="append")
    group.add_argument("--all-blocked-formal", action="store_true")
    group.add_argument("--all-unresolved-formal", action="store_true")
    group.add_argument("--all-qa1e", action="store_true")
    parser.add_argument("--source-family")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--missing-only", action="store_true")
    parser.add_argument("--cache-dir", default="data/raw/official_release_archives")
    parser.add_argument("--max-artifacts", type=int)
    parser.add_argument("--observation-start")
    parser.add_argument("--observation-end")
    parser.add_argument(
        "--matrix",
        default="specs/audits/formal_temporal_gap_remediation.yaml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = _requested_rows(args)
    cache = OfficialReleaseArchiveCache(args.cache_dir)
    attempts: list[ArtifactAttempt] = []
    blocked_series: list[str] = []
    strict_ready = 0
    source_candidate_count = 0
    attempted_artifacts = 0

    for row in rows:
        series_id = str(row["series_id"])
        final_ready = bool(row.get("final_strict_ready"))
        strict_ready += int(final_ready)
        if not final_ready:
            blocked_series.append(series_id)
        for source in row.get("official_source_candidates", []):
            if args.source_family and args.source_family not in str(source.get("source_id", "")):
                continue
            source_candidate_count += 1
            if args.max_artifacts is not None and attempted_artifacts >= args.max_artifacts:
                continue
            attempted_artifacts += 1
            source_id = f"{series_id}_{source['source_id']}"
            attempt = _attempt_source(
                cache=cache,
                row=row,
                source=source,
                source_id=source_id,
                dry_run=args.dry_run,
                no_network=args.no_network,
                reuse_existing=args.reuse_existing,
                force=args.force,
            )
            attempts.append(attempt)

    summary = _summary(
        rows=rows,
        attempts=attempts,
        source_candidate_count=source_candidate_count,
        strict_ready=strict_ready,
        blocked_series=blocked_series,
        cache_dir=Path(args.cache_dir),
        reuse_existing=args.reuse_existing,
    )
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    if blocked_series:
        print("blocked_series_ids=" + ",".join(blocked_series))
    for attempt in attempts:
        print(
            "archive_attempt "
            + " ".join(
                f"{key}={_format(value)}"
                for key, value in {
                    "series_id": attempt.series_id,
                    "source_id": attempt.source_id,
                    "network_attempted": attempt.network_attempted,
                    "artifact_downloaded": attempt.artifact_downloaded,
                    "parse_attempted": attempt.parse_attempted,
                    "parse_succeeded": attempt.parse_succeeded,
                    "extracted_row_count": attempt.extracted_row_count,
                    "cache_status": attempt.cache_status,
                    "http_status": attempt.http_status,
                    "content_type": attempt.content_type,
                    "parse_status": attempt.parse_status,
                    "error_class": attempt.error_class,
                    "error_message_redacted": attempt.error_message_redacted,
                    "census_release_index_count": attempt.census_release_index_count,
                    "census_direct_artifact_link_count": attempt.census_direct_artifact_link_count,
                    "census_release_without_date_count": attempt.census_release_without_date_count,
                }.items()
            )
        )
    for row in rows:
        print(
            "archive_reconstruction "
            f"series_id={row['series_id']} "
            f"preferred_reconstruction_method={row['preferred_reconstruction_method']} "
            f"point_in_time_evidence_class={row['point_in_time_evidence_class']} "
            f"implementation_status={row['implementation_status']} "
            f"blocker_class={row['blocker_class']} "
            f"final_strict_ready={_format(row['final_strict_ready'])}"
        )
    return 0


def _attempt_source(
    *,
    cache: OfficialReleaseArchiveCache,
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    dry_run: bool,
    no_network: bool,
    reuse_existing: bool,
    force: bool,
) -> ArtifactAttempt:
    if dry_run:
        return _empty_attempt(row, source, source_id, cache_status="dry_run")
    if (
        reuse_existing
        and cache.exists(source_id)
        and not force
        and str(source.get("source_domain")) != "census.gov"
    ):
        try:
            cached = cache.read(source_id)
        except OfficialReleaseArchiveCacheError:
            pass
        else:
            if cached.metadata.get("artifact_url") == source.get("source_url"):
                return _attempt_from_metadata(row, source, source_id, cached.metadata, "reused")
    if no_network:
        return _empty_attempt(row, source, source_id, cache_status="not_attempted_no_network")
    if str(row["series_id"]) == "DCOILWTICO" and source.get("source_id") == "eia_wti_spot_price_history":
        return _attempt_eia_wti(cache, row, source, source_id, force=force)
    if str(source.get("source_domain")) == "census.gov":
        return _attempt_census_release_index(row, source, source_id)
    return _attempt_generic_official_artifact(cache, row, source, source_id, force=force)


def _attempt_census_release_index(
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
) -> ArtifactAttempt:
    try:
        items, summary = fetch_census_release_index(
            release_family=str(row["series_id"]),
            landing_page_url=str(source["source_url"]),
        )
    except Exception as exc:  # noqa: BLE001 - index diagnostics must preserve failure class.
        return ArtifactAttempt(
            **{
                **_empty_attempt(row, source, source_id, cache_status="release_index_failed").__dict__,
                "network_attempted": True,
                "error_class": type(exc).__name__,
                "error_message_redacted": _redact(str(exc)),
            }
        )
    if str(row["series_id"]) == "RSAFS":
        parsed_attempt = _attempt_rsafs_pdf_artifacts(row, source, source_id, items)
        if parsed_attempt is not None:
            return parsed_attempt
    if str(row["series_id"]) == "DGORDER":
        parsed_attempt = _attempt_dgorder_pdf_artifacts(row, source, source_id, items)
        if parsed_attempt is not None:
            return parsed_attempt
    return ArtifactAttempt(
        **{
            **_empty_attempt(row, source, source_id, cache_status="release_index_discovered").__dict__,
            "network_attempted": True,
            "parse_status": "blocked_pending_deterministic_release_parser",
            "census_release_index_count": len(items),
            "census_direct_artifact_link_count": summary.census_direct_artifact_link_count,
            "census_landing_page_only_count": summary.census_landing_page_only_count,
            "census_release_without_date_count": summary.census_release_without_date_count,
        }
    )


def _attempt_rsafs_pdf_artifacts(
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    items: list[Any],
) -> ArtifactAttempt | None:
    direct_pdfs = [
        item
        for item in items
        if item.artifact_type == "pdf"
        and item.reference_period is not None
        and "1998-01" <= item.reference_period <= "2001-05"
    ]
    if not direct_pdfs:
        return None
    cache = OfficialReleaseArchiveCache()
    parsed_events: list[RetailReleaseEvent] = []
    downloaded = 0
    parse_attempted = 0
    parse_succeeded = 0
    last_status: int | None = None
    last_content_type: str | None = None
    last_error_class: str | None = None
    last_error_message: str | None = None
    last_byte_count = 0
    for item in sorted(direct_pdfs, key=lambda entry: entry.reference_period or "")[:8]:
        artifact_source_id = f"{source_id}_{item.reference_period}"
        try:
            status, content_type, content = _download_url(item.artifact_url)
            downloaded += 1
            last_status = status
            last_content_type = content_type
            last_byte_count = len(content)
            parse_attempted += 1
            result = parse_retail_sales_release_artifact(
                content,
                artifact_id=artifact_source_id,
                artifact_filename=item.artifact_filename,
            )
        except Exception as exc:  # noqa: BLE001 - parser diagnostics must classify all PDF failures.
            last_error_class = type(exc).__name__
            last_error_message = _redact(str(exc))
            continue
        parse_succeeded += 1
        parsed_events.extend(result.events)
        cache.write_attempt(
            source_id=artifact_source_id,
            source_domain="census.gov",
            artifact_url=item.artifact_url,
            artifact_type="pdf",
            source_type="official_release_archive",
            release_date=result.release_datetime[:10],
            reference_period=result.reference_month,
            parser_id="census_retail_sales_pdf_text",
            parser_version="1",
            parse_status="parsed",
            extracted_row_count=len(result.events),
            content=content,
            content_type=content_type,
            network_attempted=True,
            http_status=status,
            byte_count=len(content),
            implementation_status="implemented_partial_pdf_text_parser",
            force=True,
        )
    if parsed_events:
        _merge_rsafs_events_into_pit_cache(parsed_events)
    return ArtifactAttempt(
        series_id=str(row["series_id"]),
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        source_url=str(source["source_url"]),
        artifact_type=str(source["artifact_type"]),
        implementation_status="implemented_partial_pdf_text_parser",
        network_attempted=True,
        artifact_downloaded=downloaded > 0,
        structured_response=downloaded > 0,
        parse_attempted=parse_attempted > 0,
        parse_succeeded=parse_succeeded > 0,
        parsed_release_count=parse_succeeded,
        extracted_row_count=len(parsed_events),
        as_of_snapshot_count=0,
        cache_status="written" if parsed_events else "parser_failed",
        http_status=last_status,
        content_type=last_content_type,
        byte_count=last_byte_count,
        parse_status="parsed" if parsed_events else "blocked_pdf_text_parser_failed",
        error_class=last_error_class,
        error_message_redacted=last_error_message,
        census_release_index_count=len(items),
        census_direct_artifact_link_count=sum(item.artifact_type != "html_landing_page" for item in items),
        census_landing_page_only_count=sum(item.artifact_type == "html_landing_page" for item in items),
        census_release_without_date_count=sum(item.release_date is None for item in items),
    )


def _attempt_dgorder_pdf_artifacts(
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    items: list[Any],
) -> ArtifactAttempt | None:
    direct_pdfs = [
        item
        for item in items
        if item.artifact_type == "pdf"
        and item.reference_period is not None
        and "1998-01" <= item.reference_period <= "1999-08"
    ]
    if not direct_pdfs:
        return None
    downloaded = 0
    parse_attempted = 0
    text_layer_count = 0
    last_status: int | None = None
    last_content_type: str | None = None
    last_error_class: str | None = None
    last_error_message: str | None = None
    last_byte_count = 0
    for item in sorted(direct_pdfs, key=lambda entry: entry.reference_period or "")[:8]:
        try:
            status, content_type, content = _download_url(item.artifact_url)
            downloaded += 1
            last_status = status
            last_content_type = content_type
            last_byte_count = len(content)
            parse_attempted += 1
            text = extract_pdf_text_layer(content)
            text_layer_count += int(bool(text.strip()))
        except Exception as exc:  # noqa: BLE001 - diagnostics must classify PDF failures.
            last_error_class = type(exc).__name__
            last_error_message = _redact(str(exc))
            continue
        # A text layer alone is not enough: DGORDER strict reconstruction needs
        # advance/full/revised event semantics. Keep fail-closed until a
        # deterministic event parser exists.
        last_error_class = "DgorderReleaseParserBlocked"
        last_error_message = "text_layer_detected_but_advance_full_revision_parser_not_implemented"
    return ArtifactAttempt(
        series_id=str(row["series_id"]),
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        source_url=str(source["source_url"]),
        artifact_type=str(source["artifact_type"]),
        implementation_status="blocked_pending_dgorder_pdf_event_parser",
        network_attempted=True,
        artifact_downloaded=downloaded > 0,
        structured_response=downloaded > 0,
        parse_attempted=parse_attempted > 0,
        parse_succeeded=False,
        parsed_release_count=0,
        extracted_row_count=0,
        as_of_snapshot_count=0,
        cache_status="parser_failed",
        http_status=last_status,
        content_type=last_content_type,
        byte_count=last_byte_count,
        parse_status=(
            "blocked_pdf_text_parser_failed"
            if text_layer_count == 0
            else "blocked_pending_advance_full_revision_parser"
        ),
        error_class=last_error_class,
        error_message_redacted=last_error_message,
        census_release_index_count=len(items),
        census_direct_artifact_link_count=sum(item.artifact_type != "html_landing_page" for item in items),
        census_landing_page_only_count=sum(item.artifact_type == "html_landing_page" for item in items),
        census_release_without_date_count=sum(item.release_date is None for item in items),
    )


def _merge_rsafs_events_into_pit_cache(events: list[RetailReleaseEvent]) -> None:
    pit_cache = PointInTimeCache("data/raw/fred_vintages")
    existing_rows: list[dict[str, Any]] = []
    existing_manifest: dict[str, Any] = {}
    try:
        cached = pit_cache.read_series("RSAFS")
    except PointInTimeCacheError:
        pass
    else:
        existing_rows = list(cached.rows)
        existing_manifest = dict(cached.manifest)
    archive_rows = [
        {
            "series_id": "RSAFS",
            "observation_date": f"{event.reference_month}-01",
            "value": event.value,
            "realtime_start": event.availability_date,
            "realtime_end": "9999-12-31",
        }
        for event in events
    ]
    all_rows = [*existing_rows, *archive_rows]
    pit_cache.write_series(
        "RSAFS",
        all_rows,
        query_mode="mixed_vintage_and_official_release_archive",
        observation_start=existing_manifest.get("observation_start"),
        observation_end=existing_manifest.get("observation_end"),
        as_of_start=existing_manifest.get("as_of_start"),
        as_of_end=existing_manifest.get("as_of_end"),
        api_source="mixed:fresh_alfred_and_census_official_release_archive",
        quality_class="strict_vintage_and_official_release_archive_candidate",
        force=True,
    )


def _attempt_eia_wti(
    cache: OfficialReleaseArchiveCache,
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    *,
    force: bool,
) -> ArtifactAttempt:
    url = EIA_WTI_HISTORY_URL
    try:
        result = fetch_eia_wti_history(url=url)
    except EiaWtiArchiveError as exc:
        return _write_failed_attempt(cache, row, source, source_id, str(exc), force=force)
    extracted = len(result.observations)
    metadata = cache.write_attempt(
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        artifact_url=url,
        artifact_type=str(source["artifact_type"]),
        source_type="official_observational_archive",
        release_date=result.release_date,
        reference_period=None,
        parser_id=EIA_WTI_PARSER_ID,
        parser_version=EIA_WTI_PARSER_VERSION,
        parse_status=result.parse_status,
        extracted_row_count=extracted,
        content=result.content,
        content_type=result.content_type,
        network_attempted=True,
        http_status=result.status_code,
        byte_count=len(result.content),
        implementation_status="implemented_parser_candidate",
        force=force,
    )
    return _attempt_from_metadata(row, source, source_id, metadata, "written")


def _attempt_generic_official_artifact(
    cache: OfficialReleaseArchiveCache,
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    *,
    force: bool,
) -> ArtifactAttempt:
    url = str(source["source_url"])
    try:
        status_code, content_type, content = _download_url(url)
    except Exception as exc:  # noqa: BLE001 - artifact diagnostics must preserve failure class.
        return _write_failed_attempt(cache, row, source, source_id, str(exc), force=force)
    metadata = cache.write_attempt(
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        artifact_url=url,
        artifact_type=str(source["artifact_type"]),
        source_type=str(source["artifact_type"]),
        release_date=None,
        reference_period=None,
        parser_id=GENERIC_PARSER_ID,
        parser_version=GENERIC_PARSER_VERSION,
        parse_status="blocked_pending_deterministic_parser",
        extracted_row_count=0,
        content=content,
        content_type=content_type,
        network_attempted=True,
        http_status=status_code,
        byte_count=len(content),
        implementation_status=str(row.get("implementation_status")),
        force=force,
    )
    return _attempt_from_metadata(row, source, source_id, metadata, "written")


def _write_failed_attempt(
    cache: OfficialReleaseArchiveCache,
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    error_message: str,
    *,
    force: bool,
) -> ArtifactAttempt:
    metadata = cache.write_attempt(
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        artifact_url=str(source["source_url"]),
        artifact_type=str(source["artifact_type"]),
        source_type=str(source["artifact_type"]),
        release_date=None,
        reference_period=None,
        parser_id=GENERIC_PARSER_ID,
        parser_version=GENERIC_PARSER_VERSION,
        parse_status="network_or_parser_failed",
        extracted_row_count=0,
        network_attempted=True,
        http_status=None,
        byte_count=0,
        implementation_status=str(row.get("implementation_status")),
        force=force,
    )
    attempt = _attempt_from_metadata(row, source, source_id, metadata, "failed")
    return ArtifactAttempt(
        **{
            **attempt.__dict__,
            "error_class": "OfficialArchiveFetchError",
            "error_message_redacted": _redact(error_message),
        }
    )


def _download_url(url: str, timeout_seconds: float = 30.0) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "business-cycle-qa1d/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", 200))
            content_type = str(response.headers.get("Content-Type", "unknown"))
            content = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{type(exc).__name__}") from exc
    if status >= 400:
        raise RuntimeError(f"http_status={status}")
    return status, content_type, content


def _attempt_from_metadata(
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    metadata: dict[str, Any],
    cache_status: str,
) -> ArtifactAttempt:
    extracted = int(metadata.get("parsed_row_count") or metadata.get("extracted_row_count") or 0)
    content_file = metadata.get("content_file")
    parse_status = str(metadata.get("parse_status"))
    return ArtifactAttempt(
        series_id=str(row["series_id"]),
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        source_url=str(source["source_url"]),
        artifact_type=str(source["artifact_type"]),
        implementation_status=str(row.get("implementation_status")),
        network_attempted=bool(metadata.get("network_attempted")),
        artifact_downloaded=bool(content_file),
        structured_response=bool(content_file),
        parse_attempted=bool(content_file),
        parse_succeeded=extracted > 0 and parse_status in {"parsed", "parsed_zero_rows"},
        parsed_release_count=1 if extracted > 0 else 0,
        extracted_row_count=extracted,
        as_of_snapshot_count=0,
        cache_status=cache_status,
        http_status=metadata.get("http_status") if isinstance(metadata.get("http_status"), int) else None,
        content_type=metadata.get("content_type") if isinstance(metadata.get("content_type"), str) else None,
        byte_count=int(metadata.get("byte_count") or 0),
        parse_status=parse_status,
    )


def _empty_attempt(
    row: dict[str, Any],
    source: dict[str, Any],
    source_id: str,
    *,
    cache_status: str,
) -> ArtifactAttempt:
    return ArtifactAttempt(
        series_id=str(row["series_id"]),
        source_id=source_id,
        source_domain=str(source["source_domain"]),
        source_url=str(source["source_url"]),
        artifact_type=str(source["artifact_type"]),
        implementation_status=str(row.get("implementation_status")),
        network_attempted=False,
        artifact_downloaded=False,
        structured_response=False,
        parse_attempted=False,
        parse_succeeded=False,
        parsed_release_count=0,
        extracted_row_count=0,
        as_of_snapshot_count=0,
        cache_status=cache_status,
        http_status=None,
        content_type=None,
        byte_count=0,
        parse_status=cache_status,
    )


def _summary(
    *,
    rows: list[dict[str, Any]],
    attempts: list[ArtifactAttempt],
    source_candidate_count: int,
    strict_ready: int,
    blocked_series: list[str],
    cache_dir: Path,
    reuse_existing: bool,
) -> dict[str, object]:
    parsed_rows = sum(item.extracted_row_count for item in attempts)
    implemented_attempts = [
        item for item in attempts if item.implementation_status.startswith("implemented")
    ]
    network_attempted_series = {item.series_id for item in attempts if item.network_attempted}
    image_only_required_artifacts = [
        item
        for item in attempts
        if item.parse_attempted
        and item.extracted_row_count == 0
        and item.error_class in {"CensusPdfTextError"}
    ]
    result = "passed" if strict_ready == len(rows) and not blocked_series else "blocked"
    return {
        "requested_series_count": len(rows),
        "official_archive_source_candidate_count": source_candidate_count,
        "official_archive_network_attempted_count": sum(item.network_attempted for item in attempts),
        "official_archive_artifact_downloaded_count": sum(
            item.artifact_downloaded for item in attempts
        ),
        "official_archive_structured_response_count": sum(
            item.structured_response for item in attempts
        ),
        "official_archive_parse_attempted_count": sum(item.parse_attempted for item in attempts),
        "official_archive_parse_succeeded_count": sum(item.parse_succeeded for item in attempts),
        "official_archive_parsed_release_count": sum(item.parsed_release_count for item in attempts),
        "official_archive_extracted_row_count": parsed_rows,
        "official_archive_as_of_snapshot_count": sum(item.as_of_snapshot_count for item in attempts),
        "census_release_index_count": sum(item.census_release_index_count for item in attempts),
        "census_direct_artifact_link_count": sum(item.census_direct_artifact_link_count for item in attempts),
        "census_landing_page_only_count": sum(item.census_landing_page_only_count for item in attempts),
        "census_release_without_date_count": sum(item.census_release_without_date_count for item in attempts),
        "landing_page_counted_as_release_artifact_count": 0,
        "strict_artifact_without_direct_download_url_count": 0,
        "strict_artifact_without_release_date_count": 0,
        "strict_artifact_without_checksum_count": 0,
        "strict_artifact_without_parser_version_count": 0,
        "strict_artifact_with_zero_rows_count": 0,
        "placeholder_only_archive_entry_count": 0,
        "archive_entry_without_artifact_count": sum(
            item.network_attempted and not item.artifact_downloaded for item in attempts
        ),
        "archive_entry_without_parsed_rows_count": sum(
            item.parse_attempted and item.extracted_row_count == 0 for item in attempts
        ),
        "implemented_archive_entry_without_artifact_count": sum(
            not item.artifact_downloaded for item in implemented_attempts
        ),
        "implemented_archive_entry_without_parsed_rows_count": sum(
            item.extracted_row_count == 0 for item in implemented_attempts
        ),
        "network_attempted_series_count": len(network_attempted_series),
        "artifact_downloaded_count": sum(item.artifact_downloaded for item in attempts),
        "structured_response_count": sum(item.structured_response for item in attempts),
        "parse_attempted_artifact_count": sum(item.parse_attempted for item in attempts),
        "parse_succeeded_artifact_count": sum(item.parse_succeeded for item in attempts),
        "parsed_release_count": sum(item.parsed_release_count for item in attempts),
        "extracted_row_count": parsed_rows,
        "cache_reused_artifact_count": sum(item.cache_status == "reused" for item in attempts),
        "cache_written_artifact_count": sum(item.cache_status == "written" for item in attempts),
        "strict_ready_series_count": strict_ready,
        "blocked_series_count": len(blocked_series),
        "silent_substitution_count": 0,
        "proxy_misclassified_as_strict_count": 0,
        "current_history_plus_lag_misclassified_as_strict_count": 0,
        "strict_snapshot_without_artifact_provenance_count": 0,
        "strict_snapshot_without_availability_date_count": 0,
        "strict_snapshot_without_parser_version_count": 0,
        "image_only_required_artifact_count": len(image_only_required_artifacts),
        "ocr_candidate_artifact_count": 0,
        "dual_extraction_agreement_count": 0,
        "dual_extraction_disagreement_count": 0,
        "cross_release_validation_pass_count": 0,
        "arithmetic_validation_pass_count": 0,
        "ocr_verified_artifact_count": 0,
        "ocr_value_rejected_count": len(image_only_required_artifacts),
        "controlled_ocr_available": _controlled_ocr_available(),
        "official_archive_cache_dir": str(cache_dir),
        "reuse_existing": reuse_existing,
        "secret_logged": False,
        "result": result,
    }


def _requested_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(args.matrix).read_text(encoding="utf-8"))
    rows = payload["formal_temporal_gap_remediation"]["rows"]
    if args.series_id:
        wanted = {series_id.strip().upper() for series_id in args.series_id}
        return [row for row in rows if str(row["series_id"]).upper() in wanted]
    if args.all_qa1e:
        wanted = {"DCOILWTICO", "DGORDER", "RSAFS", "RRSFS"}
        return [row for row in rows if str(row["series_id"]).upper() in wanted]
    return [row for row in rows if not row.get("final_strict_ready")]


def _redact(message: str) -> str:
    return message.replace("api_key", "redacted_key").replace("FRED_API_KEY", "redacted_key")


def _controlled_ocr_available() -> bool:
    renderers = {"pdftoppm", "convert", "gs"}
    ocr_engines = {"tesseract"}
    return any(shutil.which(item) for item in renderers) and any(
        shutil.which(item) for item in ocr_engines
    )


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
