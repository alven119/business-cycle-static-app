#!/usr/bin/env python
"""Show Phase 127 calendar-gate closure."""

from business_cycle.audits.phase127_prospective_calendar_gate_closure import (
    summarize_phase127_prospective_calendar_gate_closure,
)


def main() -> int:
    summary = summarize_phase127_prospective_calendar_gate_closure()
    for key, value in summary.items():
        if not isinstance(value, (dict, list)):
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
