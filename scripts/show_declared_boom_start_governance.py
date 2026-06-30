#!/usr/bin/env python
"""Show declared boom start-governance readiness."""

from __future__ import annotations

from business_cycle.cycle_state.declared_boom_start_governance import (
    summarize_declared_boom_start_governance,
)


def main() -> int:
    summary = summarize_declared_boom_start_governance()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
