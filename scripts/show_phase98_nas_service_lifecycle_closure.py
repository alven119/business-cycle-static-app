#!/usr/bin/env python
"""Show Phase98 NAS service lifecycle closure."""

from __future__ import annotations

from business_cycle.audits.phase98_nas_service_lifecycle_closure import (
    summarize_phase98_nas_service_lifecycle_closure,
)


def main() -> int:
    summary = summarize_phase98_nas_service_lifecycle_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
