#!/usr/bin/env python
"""Show Phase 39 current snapshot source availability."""

from __future__ import annotations

from business_cycle.current.current_snapshot_availability import (
    summarize_current_snapshot_availability,
)


def main() -> None:
    summary = summarize_current_snapshot_availability()
    for key, value in summary.items():
        print(f"{key}={_format_value(value)}")


def _format_value(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    main()
