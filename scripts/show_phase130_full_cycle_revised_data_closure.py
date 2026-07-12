#!/usr/bin/env python
"""Show Phase 130 full-cycle revised data closure."""

from business_cycle.audits.phase130_full_cycle_revised_data_closure import (
    summarize_phase130_full_cycle_revised_data_closure,
)


def main() -> int:
    summary = summarize_phase130_full_cycle_revised_data_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
