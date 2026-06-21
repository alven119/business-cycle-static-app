#!/usr/bin/env python
"""Show concise formal archive reconstruction status by series."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from business_cycle.storage.official_release_archive_cache import OfficialReleaseArchiveCache


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default="data/raw/official_release_archives")
    parser.add_argument(
        "--matrix",
        default="specs/audits/formal_temporal_gap_remediation.yaml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = _rows(args.matrix)
    cache = OfficialReleaseArchiveCache(args.cache_dir)
    artifacts = cache.cached_artifacts() if Path(args.cache_dir).exists() else []
    by_series: dict[str, list[dict[str, Any]]] = {}
    for artifact in artifacts:
        series_id = artifact.source_id.split("_", 1)[0]
        by_series.setdefault(series_id, []).append(artifact.metadata)

    total_artifacts = len(artifacts)
    parsed_rows = sum(int(item.metadata.get("parsed_row_count") or 0) for item in artifacts)
    parsed_artifacts = sum(int(item.metadata.get("parsed_row_count") or 0) > 0 for item in artifacts)
    print(f"official_archive_cached_artifact_count={total_artifacts}")
    print(f"official_archive_parsed_artifact_count={parsed_artifacts}")
    print(f"official_archive_extracted_row_count={parsed_rows}")
    print("secret_logged=false")
    for row in rows:
        series_id = str(row["series_id"])
        series_artifacts = by_series.get(series_id, [])
        downloaded = sum(bool(item.get("content_file")) for item in series_artifacts)
        rows_extracted = sum(int(item.get("parsed_row_count") or 0) for item in series_artifacts)
        statuses = sorted({str(item.get("parse_status")) for item in series_artifacts})
        print(
            "archive_status "
            f"series_id={series_id} "
            f"artifact_count={len(series_artifacts)} "
            f"downloaded_artifact_count={downloaded} "
            f"extracted_row_count={rows_extracted} "
            f"implementation_status={row['implementation_status']} "
            f"final_strict_ready={_format(row['final_strict_ready'])} "
            f"parse_statuses={','.join(statuses) if statuses else 'none'}"
        )
    return 0


def _rows(path: str) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["formal_temporal_gap_remediation"]["rows"]


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
