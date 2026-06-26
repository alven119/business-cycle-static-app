#!/usr/bin/env python
"""Show Phase 39 current research snapshot audit."""

from __future__ import annotations

from business_cycle.audits.phase39_current_research_snapshot import (
    summarize_phase39_current_research_snapshot,
)


def main() -> None:
    summary = summarize_phase39_current_research_snapshot()
    for key, value in summary.items():
        if key in {"snapshot"}:
            continue
        print(f"{key}={_format_value(value)}")


def _format_value(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    main()
