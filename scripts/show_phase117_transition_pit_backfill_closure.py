#!/usr/bin/env python
"""Show Phase 117 transition PIT and release-calendar closure."""

from business_cycle.audits.phase117_transition_pit_backfill_closure import (
    summarize_phase117_transition_pit_backfill_closure,
)


def main() -> int:
    summary = summarize_phase117_transition_pit_backfill_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
