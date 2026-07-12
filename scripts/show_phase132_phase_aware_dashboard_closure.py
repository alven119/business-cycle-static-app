#!/usr/bin/env python
"""Show Phase 132 closure."""

from business_cycle.audits.phase132_phase_aware_dashboard_closure import (
    summarize_phase132_phase_aware_dashboard_closure,
)


def main() -> int:
    summary = summarize_phase132_phase_aware_dashboard_closure()
    for key, value in summary.items():
        if key != "matrix_rows":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
