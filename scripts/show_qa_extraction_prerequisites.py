#!/usr/bin/env python
"""Show QA extraction prerequisite status."""

from __future__ import annotations

from dataclasses import asdict

from business_cycle.data_sources.extraction_prerequisites import (
    summarize_extraction_prerequisites,
)


def main() -> int:
    summary = asdict(summarize_extraction_prerequisites())
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
