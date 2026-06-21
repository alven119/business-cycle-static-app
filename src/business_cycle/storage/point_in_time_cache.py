"""Filesystem cache for point-in-time vintage observations."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class PointInTimeCacheError(ValueError):
    """Raised when a point-in-time cache file is invalid."""


@dataclass(frozen=True)
class CachedSeries:
    """Parsed cached vintage rows and manifest metadata."""

    series_id: str
    rows: list[dict[str, str]]
    manifest: dict[str, Any]


class PointInTimeCache:
    """CSV plus JSON-manifest cache for ALFRED/FRED vintage observations."""

    schema_version = 1
    fieldnames = ("series_id", "observation_date", "value", "realtime_start", "realtime_end")

    def __init__(self, root_dir: str | Path = "data/raw/fred_vintages") -> None:
        self.root_dir = Path(root_dir)

    def csv_path(self, series_id: str) -> Path:
        return self.root_dir / f"{_clean_series_id(series_id)}.csv"

    def manifest_path(self, series_id: str) -> Path:
        return self.root_dir / f"{_clean_series_id(series_id)}.manifest.json"

    def exists(self, series_id: str) -> bool:
        return self.csv_path(series_id).exists() and self.manifest_path(series_id).exists()

    def write_series(
        self,
        series_id: str,
        rows: Iterable[dict[str, Any]],
        *,
        query_mode: str,
        observation_start: str | None,
        observation_end: str | None,
        as_of_start: str | None,
        as_of_end: str | None,
        api_source: str = "fred/series/observations",
        quality_class: str = "strict_vintage_candidate",
        segment_metadata: list[dict[str, Any]] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Validate, deduplicate, and atomically write cache files."""

        clean_series_id = _clean_series_id(series_id)
        if self.exists(clean_series_id) and not force:
            return self.read_series(clean_series_id).manifest

        normalized, duplicate_row_count = _dedupe_rows(clean_series_id, rows)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.csv_path(clean_series_id)
        manifest_path = self.manifest_path(clean_series_id)
        csv_tmp = csv_path.with_suffix(".csv.tmp")
        manifest_tmp = manifest_path.with_suffix(".json.tmp")

        with csv_tmp.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(normalized)

        checksum = _sha256(csv_tmp)
        manifest = {
            "schema_version": self.schema_version,
            "series_id": clean_series_id,
            "query_mode": query_mode,
            "observation_start": observation_start,
            "observation_end": observation_end,
            "as_of_start": as_of_start,
            "as_of_end": as_of_end,
            "fetched_at": _now_iso(),
            "row_count": len(normalized),
            "duplicate_row_count": duplicate_row_count,
            "checksum": checksum,
            "api_source": api_source,
            "point_in_time_quality_class": quality_class,
            "earliest_observation_date": _min_field(normalized, "observation_date"),
            "latest_observation_date": _max_field(normalized, "observation_date"),
            "earliest_realtime_start": _min_field(normalized, "realtime_start"),
            "latest_realtime_start": _max_field(normalized, "realtime_start"),
            "deduplication_key": [
                "series_id",
                "observation_date",
                "realtime_start",
                "realtime_end",
            ],
            "segmented_cache": bool(segment_metadata),
            "segment_count": len(segment_metadata or []),
            "segments": segment_metadata or [],
            "segment_merge_failure_count": 0,
            "secret_logged": False,
        }
        _assert_no_secret(manifest)
        manifest_tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(csv_tmp, csv_path)
        os.replace(manifest_tmp, manifest_path)
        return manifest

    def consolidate_segmented_vintage_cache(
        self,
        series_id: str,
        segment_rows: Iterable[Iterable[dict[str, Any]]],
        *,
        query_mode: str,
        observation_start: str | None,
        observation_end: str | None,
        as_of_start: str | None,
        as_of_end: str | None,
        segment_metadata: list[dict[str, Any]],
        force: bool = False,
    ) -> dict[str, Any]:
        """Merge segmented vintage rows into one authoritative cache atomically."""

        rows = merge_point_in_time_rows(series_id, segment_rows)
        validation = validate_segment_union(segment_metadata)
        manifest = self.write_series(
            series_id,
            rows,
            query_mode=query_mode,
            observation_start=observation_start,
            observation_end=observation_end,
            as_of_start=as_of_start,
            as_of_end=as_of_end,
            segment_metadata=segment_metadata,
            force=force,
        )
        manifest["segment_validation"] = validation
        manifest_tmp = self.manifest_path(series_id).with_suffix(".json.tmp")
        _assert_no_secret(manifest)
        manifest_tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(manifest_tmp, self.manifest_path(series_id))
        return manifest

    def read_series(self, series_id: str) -> CachedSeries:
        """Read and validate cached rows."""

        clean_series_id = _clean_series_id(series_id)
        csv_path = self.csv_path(clean_series_id)
        manifest_path = self.manifest_path(clean_series_id)
        if not csv_path.exists() or not manifest_path.exists():
            raise PointInTimeCacheError(f"Missing point-in-time cache for {clean_series_id}")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PointInTimeCacheError(f"Corrupt manifest for {clean_series_id}") from exc
        if manifest.get("schema_version") != self.schema_version:
            raise PointInTimeCacheError(f"Unsupported cache schema for {clean_series_id}")
        if manifest.get("checksum") != _sha256(csv_path):
            raise PointInTimeCacheError(f"Checksum mismatch for {clean_series_id}")

        with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
            rows = [dict(row) for row in csv.DictReader(csv_file)]
        normalized, duplicate_row_count = _dedupe_rows(clean_series_id, rows)
        if duplicate_row_count:
            raise PointInTimeCacheError(f"Duplicate rows detected for {clean_series_id}")
        if int(manifest.get("row_count", -1)) != len(rows):
            raise PointInTimeCacheError(f"Row count mismatch for {clean_series_id}")
        _assert_no_secret(manifest)
        return CachedSeries(series_id=clean_series_id, rows=rows, manifest=manifest)

    def cached_series_ids(self) -> set[str]:
        """Return series IDs with both CSV and manifest present."""

        ids = {path.stem for path in self.root_dir.glob("*.csv")}
        return {series_id for series_id in ids if self.manifest_path(series_id).exists()}

    def explain_cache_coverage(self, series_id: str) -> dict[str, Any]:
        """Return manifest-backed coverage diagnostics for one cached series."""

        cached = self.read_series(series_id)
        manifest = cached.manifest
        return {
            "series_id": cached.series_id,
            "cache_path": str(self.csv_path(series_id)),
            "manifest_path": str(self.manifest_path(series_id)),
            "cache_manifest_checksum_valid": True,
            "row_count": manifest.get("row_count"),
            "query_mode": manifest.get("query_mode"),
            "observation_start": manifest.get("observation_start"),
            "observation_end": manifest.get("observation_end"),
            "as_of_start": manifest.get("as_of_start"),
            "as_of_end": manifest.get("as_of_end"),
            "earliest_observation_date": manifest.get("earliest_observation_date"),
            "latest_observation_date": manifest.get("latest_observation_date"),
            "earliest_realtime_start": manifest.get("earliest_realtime_start"),
            "latest_realtime_start": manifest.get("latest_realtime_start"),
            "segmented_cache": manifest.get("segmented_cache", False),
            "segment_count": manifest.get("segment_count", 0),
            "segment_merge_failure_count": manifest.get("segment_merge_failure_count", 0),
        }


def merge_point_in_time_rows(
    series_id: str,
    segment_rows: Iterable[Iterable[dict[str, Any]]],
) -> list[dict[str, str]]:
    """Merge segmented rows with strict conflict detection."""

    clean_series_id = _clean_series_id(series_id)
    merged: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for rows in segment_rows:
        normalized, _duplicate_count = _dedupe_rows(clean_series_id, rows)
        for item in normalized:
            key = (
                item["series_id"],
                item["observation_date"],
                item["realtime_start"],
                item["realtime_end"],
            )
            existing = merged.get(key)
            if existing is not None and existing["value"] != item["value"]:
                raise PointInTimeCacheError(
                    f"Conflicting segmented values for {clean_series_id} key={key}"
                )
            merged[key] = item
    return sorted(
        merged.values(),
        key=lambda item: (
            item["observation_date"],
            item["realtime_start"],
            item["realtime_end"],
        ),
    )


def validate_segment_union(segment_metadata: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate basic segmented cache metadata without requiring full horizon coverage."""

    sorted_segments = sorted(
        segment_metadata,
        key=lambda item: str(item.get("realtime_start") or item.get("segment_start") or ""),
    )
    gap_count = 0
    overlap_count = 0
    previous_end: str | None = None
    for segment in sorted_segments:
        start = str(segment.get("realtime_start") or segment.get("segment_start") or "")
        end = str(segment.get("realtime_end") or segment.get("segment_end") or "")
        if previous_end and start <= previous_end:
            overlap_count += 1
        previous_end = end or previous_end
    return {
        "segment_count": len(sorted_segments),
        "segment_gap_count": gap_count,
        "segment_overlap_count": overlap_count,
    }


def _dedupe_rows(series_id: str, rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, str]], int]:
    normalized: list[dict[str, str]] = []
    seen: dict[tuple[str, str, str, str], str] = {}
    duplicate_row_count = 0
    for row in rows:
        item = {
            "series_id": _clean_series_id(str(row.get("series_id") or series_id)),
            "observation_date": str(row.get("observation_date") or row.get("date") or ""),
            "value": str(row.get("value") or ""),
            "realtime_start": str(row.get("realtime_start") or ""),
            "realtime_end": str(row.get("realtime_end") or ""),
        }
        if not all(item[field] for field in ("series_id", "observation_date", "value", "realtime_start")):
            raise PointInTimeCacheError(f"Cache row missing required fields for {series_id}")
        key = (
            item["series_id"],
            item["observation_date"],
            item["realtime_start"],
            item["realtime_end"],
        )
        existing_value = seen.get(key)
        if existing_value is not None:
            if existing_value != item["value"]:
                raise PointInTimeCacheError(
                    f"Conflicting duplicate values detected for {series_id} key={key}"
                )
            duplicate_row_count += 1
            continue
        seen[key] = item["value"]
        normalized.append(item)
    return (
        sorted(
            normalized,
            key=lambda item: (
                item["observation_date"],
                item["realtime_start"],
                item["realtime_end"],
            ),
        ),
        duplicate_row_count,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_no_secret(value: Any) -> None:
    text = json.dumps(value, sort_keys=True)
    if "FRED_API_KEY" in text or "api_key" in text.lower():
        raise PointInTimeCacheError("Cache metadata must not contain API keys")


def _clean_series_id(series_id: str) -> str:
    return series_id.strip().upper()


def _min_field(rows: list[dict[str, str]], field: str) -> str | None:
    values = [row[field] for row in rows if row.get(field)]
    return min(values) if values else None


def _max_field(rows: list[dict[str, str]], field: str) -> str | None:
    values = [row[field] for row in rows if row.get(field)]
    return max(values) if values else None


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
