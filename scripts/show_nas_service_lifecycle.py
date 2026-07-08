#!/usr/bin/env python
"""Show Phase98 NAS service lifecycle readiness."""

from __future__ import annotations

from business_cycle.service.nas_service_lifecycle import (
    summarize_nas_service_lifecycle,
)


def main() -> int:
    summary = summarize_nas_service_lifecycle()
    for key, value in summary.items():
        if key == "nas_service_lifecycle":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
