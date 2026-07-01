#!/usr/bin/env python
"""Show Phase54 low-cost macro source completion."""

from __future__ import annotations

from business_cycle.audits.low_cost_macro_source_completion import (
    summarize_low_cost_macro_source_completion,
)


def main() -> int:
    summary = summarize_low_cost_macro_source_completion()
    for key, value in summary.items():
        if key == "rows":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
