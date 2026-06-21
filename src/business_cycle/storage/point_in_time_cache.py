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
        force: bool = False,
    ) -> dict[str, Any]:
        """Validate, deduplicate, and atomically write cache files."""

        clean_series_id = _clean_series_id(series_id)
        if self.exists(clean_series_id) and not force:
            return self.read_series(clean_series_id).manifest

        normalized = _dedupe_rows(clean_series_id, rows)
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
            "checksum": checksum,
            "api_source": api_source,
            "point_in_time_quality_class": quality_class,
            "deduplication_key": [
                "series_id",
                "observation_date",
                "realtime_start",
                "realtime_end",
            ],
            "secret_logged": False,
        }
        _assert_no_secret(manifest)
        manifest_tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(csv_tmp, csv_path)
        os.replace(manifest_tmp, manifest_path)
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
        _dedupe_rows(clean_series_id, rows)
        if int(manifest.get("row_count", -1)) != len(rows):
            raise PointInTimeCacheError(f"Row count mismatch for {clean_series_id}")
        _assert_no_secret(manifest)
        return CachedSeries(series_id=clean_series_id, rows=rows, manifest=manifest)

    def cached_series_ids(self) -> set[str]:
        """Return series IDs with both CSV and manifest present."""

        ids = {path.stem for path in self.root_dir.glob("*.csv")}
        return {series_id for series_id in ids if self.manifest_path(series_id).exists()}


def _dedupe_rows(series_id: str, rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
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
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return sorted(
        normalized,
        key=lambda item: (
            item["observation_date"],
            item["realtime_start"],
            item["realtime_end"],
        ),
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
