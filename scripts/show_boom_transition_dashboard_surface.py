#!/usr/bin/env python
"""Show Phase49 boom transition dashboard surface gates."""

from __future__ import annotations

from business_cycle.render.boom_transition_dashboard_surface import (
    summarize_boom_transition_dashboard_surface,
)


def main() -> int:
    summary = summarize_boom_transition_dashboard_surface()
    for key, value in summary.items():
        if key == "surface":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
