#!/usr/bin/env python
"""Show Phase 131 closure."""

from business_cycle.audits.phase131_historical_pit_transition_events_closure import (
    summarize_phase131_historical_pit_transition_events_closure,
)


def main() -> int:
    summary = summarize_phase131_historical_pit_transition_events_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
