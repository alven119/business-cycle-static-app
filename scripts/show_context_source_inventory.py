#!/usr/bin/env python
"""Show QA2 context-source inventory."""

from __future__ import annotations

from business_cycle.audits.context_source_inventory import (
    summarize_context_source_inventory,
)


def main() -> int:
    summary = summarize_context_source_inventory()
    for key, value in summary.items():
        if key == "context_sources":
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
