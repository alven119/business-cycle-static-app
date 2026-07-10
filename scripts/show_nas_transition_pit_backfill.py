#!/usr/bin/env python
"""Show Phase 117 transition-critical PIT and release-calendar readiness."""

from business_cycle.storage.nas_transition_pit_backfill import (
    summarize_nas_transition_pit_backfill_contract,
)


def main() -> int:
    summary = summarize_nas_transition_pit_backfill_contract()
    for key, value in summary.items():
        if key != "normalized_release_calendar_plan":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
