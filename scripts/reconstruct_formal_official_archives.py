#!/usr/bin/env python
"""Record QA1C official archive reconstruction attempts for formal blockers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from business_cycle.storage.official_release_archive_cache import (
    OfficialReleaseArchiveCache,
)

PARSER_ID = "qa1c_archive_reconstruction_stub"
PARSER_VERSION = "1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--series-id", action="append")
    group.add_argument("--all-blocked-formal", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cache-dir", default="data/raw/official_release_archives")
    parser.add_argument(
        "--matrix",
        default="specs/audits/formal_temporal_gap_remediation.yaml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = _requested_rows(args)
    cache = OfficialReleaseArchiveCache(args.cache_dir)
    attempted = reused = written = failed = strict_ready = 0
    blocked_series: list[str] = []
    source_candidate_count = 0

    for row in rows:
        series_id = str(row["series_id"])
        final_ready = bool(row.get("final_strict_ready"))
        strict_ready += int(final_ready)
        if not final_ready:
            blocked_series.append(series_id)
        for source in row.get("official_source_candidates", []):
            source_candidate_count += 1
            source_id = f"{series_id}_{source['source_id']}"
            if args.reuse_existing and cache.exists(source_id) and not args.force:
                reused += 1
                continue
            if args.dry_run:
                continue
            attempted += 1
            try:
                cache.write_attempt(
                    source_id=source_id,
                    source_domain=str(source["source_domain"]),
                    artifact_url=str(source["source_url"]),
                    artifact_type=str(source["artifact_type"]),
                    release_date=None,
                    reference_period=None,
                    parser_id=PARSER_ID,
                    parser_version=PARSER_VERSION,
                    parse_status=str(row.get("implementation_status")),
                    extracted_row_count=0,
                    force=args.force,
                )
            except Exception:
                failed += 1
            else:
                written += 1

    result = "passed" if strict_ready == len(rows) and failed == 0 else "blocked"
    summary = {
        "requested_series_count": len(rows),
        "source_candidate_count": source_candidate_count,
        "archive_query_attempted_series_count": 0,
        "archive_artifact_attempt_count": attempted,
        "archive_artifact_reused_count": reused,
        "archive_artifact_written_count": written,
        "archive_artifact_failed_count": failed,
        "network_request_count": 0,
        "no_network": True,
        "reuse_existing": args.reuse_existing,
        "strict_ready_series_count": strict_ready,
        "blocked_series_count": len(blocked_series),
        "official_archive_cache_dir": str(Path(args.cache_dir)),
        "secret_logged": False,
        "result": result,
    }
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    if blocked_series:
        print("blocked_series_ids=" + ",".join(blocked_series))
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


def _requested_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(args.matrix).read_text(encoding="utf-8"))
    rows = payload["formal_temporal_gap_remediation"]["rows"]
    if args.series_id:
        wanted = {series_id.strip().upper() for series_id in args.series_id}
        return [row for row in rows if str(row["series_id"]).upper() in wanted]
    return [row for row in rows if not row.get("final_strict_ready")]


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
