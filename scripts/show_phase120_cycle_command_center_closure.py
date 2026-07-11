#!/usr/bin/env python
"""Show Phase 120 command-center closure."""

from business_cycle.audits.phase120_cycle_command_center_closure import (
    summarize_phase120_cycle_command_center_closure,
)


def main() -> int:
    summary = summarize_phase120_cycle_command_center_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
