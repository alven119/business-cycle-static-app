#!/usr/bin/env python
"""Show Phase 131 PIT gap and event registry."""

from business_cycle.validation.historical_pit_transition_events import (
    build_historical_pit_transition_event_registry,
)


def main() -> int:
    summary = build_historical_pit_transition_event_registry()
    for key, value in summary.items():
        if key not in {"scenario_status", "gap_rows", "event_rows"}:
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
