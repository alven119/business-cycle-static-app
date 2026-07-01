#!/usr/bin/env python
"""Show Phase53 composite transition-surface value wiring."""

from __future__ import annotations

from business_cycle.current.composite_transition_surface_values import (
    summarize_composite_transition_surface_value_wiring,
)


def main() -> int:
    summary = summarize_composite_transition_surface_value_wiring()
    for key, value in summary.items():
        if key == "rows":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
