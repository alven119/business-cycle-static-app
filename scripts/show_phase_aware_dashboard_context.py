#!/usr/bin/env python
"""Show Phase 132 context contract."""

from business_cycle.render.phase_aware_dashboard_context import (
    summarize_phase_aware_dashboard_context,
)


def main() -> int:
    summary = summarize_phase_aware_dashboard_context()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
