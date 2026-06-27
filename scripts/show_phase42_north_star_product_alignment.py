#!/usr/bin/env python
"""Show Phase 42 North Star product alignment."""

from __future__ import annotations

from business_cycle.audits.phase42_north_star_product_alignment import (
    summarize_phase42_north_star_product_alignment,
)


def main() -> int:
    summary = summarize_phase42_north_star_product_alignment()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
