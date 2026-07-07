#!/usr/bin/env python3
"""Show Phase85 current data refresh UX closure summary."""

from __future__ import annotations

from business_cycle.audits.phase85_current_data_refresh_ux_closure import (
    summarize_phase85_current_data_refresh_ux_closure,
)


def main() -> int:
    summary = summarize_phase85_current_data_refresh_ux_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
