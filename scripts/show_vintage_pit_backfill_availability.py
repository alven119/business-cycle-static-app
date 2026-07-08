#!/usr/bin/env python
"""Show Phase 93 vintage/PIT backfill availability accounting."""

from __future__ import annotations

from business_cycle.storage.vintage_pit_backfill_availability import (
    summarize_vintage_pit_backfill_availability,
)


def main() -> int:
    summary = summarize_vintage_pit_backfill_availability()
    for key, value in summary.items():
        if key == "vintage_pit_backfill_availability_manifest":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
