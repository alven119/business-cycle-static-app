#!/usr/bin/env python
"""Show Phase108 NAS Container Manager live-start package readiness."""

from __future__ import annotations

from business_cycle.service.nas_container_manager_live_start import (
    summarize_nas_container_manager_live_start,
)


def main() -> int:
    summary = summarize_nas_container_manager_live_start()
    for key, value in summary.items():
        if key == "nas_container_manager_live_start_package":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
