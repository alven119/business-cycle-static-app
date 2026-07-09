#!/usr/bin/env python
"""Show Phase108 NAS Container Manager live-start package closure."""

from __future__ import annotations

from business_cycle.audits.phase108_nas_container_manager_live_start_closure import (
    summarize_phase108_nas_container_manager_live_start_closure,
)


def main() -> int:
    summary = summarize_phase108_nas_container_manager_live_start_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
