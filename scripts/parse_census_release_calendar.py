#!/usr/bin/env python
"""Parse the official Census MARTS release-date workbook."""

from __future__ import annotations

import argparse
import urllib.request
from dataclasses import asdict
from pathlib import Path

from business_cycle.data_sources.census_release_calendar import (
    MARTS_RELEASE_DATES_URL,
    CensusReleaseCalendarError,
    parse_marts_release_calendar_workbook,
    summarize_release_calendar,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--download-if-missing", action="store_true", default=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workbook = Path(args.workbook)
    if not workbook.exists() and args.download_if_missing:
        workbook.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            MARTS_RELEASE_DATES_URL,
            headers={"User-Agent": "business-cycle-qa1e2/1"},
        )
        with urllib.request.urlopen(request, timeout=30.0) as response:
            workbook.write_bytes(response.read())
    try:
        result = parse_marts_release_calendar_workbook(workbook)
        required = [f"{year}-{month:02d}" for year in range(1997, 2002) for month in range(1, 13)]
        summary = summarize_release_calendar(result.rows, required_reference_months=required)
        payload = {
            **asdict(summary),
            "workbook": str(workbook),
            "source_url": MARTS_RELEASE_DATES_URL,
            "source_workbook_id": result.source_workbook_id,
            "source_checksum": result.source_checksum,
            "parse_status": result.parse_status,
            "result": "passed",
        }
    except CensusReleaseCalendarError as exc:
        payload = {
            "release_calendar_artifact_count": int(workbook.exists()),
            "release_calendar_sheet_count": 0,
            "release_calendar_row_count": 0,
            "required_reference_month_count": 0,
            "required_reference_month_covered_count": 0,
            "required_reference_month_missing_count": 0,
            "duplicate_reference_month_count": 0,
            "invalid_release_date_count": 0,
            "directory_mtime_used_as_release_date_count": 0,
            "workbook": str(workbook),
            "source_url": MARTS_RELEASE_DATES_URL,
            "parse_status": "blocked",
            "blocker_reason": str(exc),
            "result": "blocked",
        }
    for key, value in payload.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
