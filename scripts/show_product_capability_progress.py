#!/usr/bin/env python
"""Show governed product capability progress."""

from __future__ import annotations

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)


def main() -> int:
    summary = summarize_product_capability_progress()
    for key, value in summary.items():
        if key == "capability_progress":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
