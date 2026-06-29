#!/usr/bin/env python
"""Show Phase46 boom transition monitor summary."""

from __future__ import annotations

from business_cycle.transition_monitor.boom_transition_monitor import (
    summarize_boom_transition_monitor,
)


def main() -> int:
    summary = summarize_boom_transition_monitor()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
