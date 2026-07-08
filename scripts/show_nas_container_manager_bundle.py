#!/usr/bin/env python
"""Show Phase100 Container Manager bundle dry-run readiness."""

from __future__ import annotations

from business_cycle.service.nas_container_manager_bundle import (
    summarize_nas_container_manager_bundle,
)


def main() -> int:
    summary = summarize_nas_container_manager_bundle()
    for key, value in summary.items():
        if key == "nas_container_manager_bundle":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
