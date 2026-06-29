#!/usr/bin/env python
"""Show the declared current cycle state registry summary."""

from __future__ import annotations

from business_cycle.cycle_state.declared_phase_registry import (
    summarize_declared_cycle_state,
)


def main() -> int:
    summary = summarize_declared_cycle_state()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
