#!/usr/bin/env python3
"""Show Phase85 current data refresh UX summary."""

from __future__ import annotations

from business_cycle.render.current_data_refresh_ux import (
    summarize_current_data_refresh_ux,
)


def main() -> int:
    summary = summarize_current_data_refresh_ux()
    for key, value in summary.items():
        if key == "current_data_refresh_ux_artifact":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
