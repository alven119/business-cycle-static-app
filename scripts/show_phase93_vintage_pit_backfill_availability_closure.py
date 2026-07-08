#!/usr/bin/env python
"""Show Phase 93 vintage/PIT backfill availability closure."""

from __future__ import annotations

from business_cycle.audits.phase93_vintage_pit_backfill_availability_closure import (
    summarize_phase93_vintage_pit_backfill_availability_closure,
)


def main() -> int:
    summary = summarize_phase93_vintage_pit_backfill_availability_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
