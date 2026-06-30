#!/usr/bin/env python
"""Show macro indicator gap alternative-source inventory."""

from __future__ import annotations

from business_cycle.audits.macro_indicator_gap_alternative_sources import (
    summarize_macro_indicator_gap_alternative_sources,
)


def main() -> int:
    summary = summarize_macro_indicator_gap_alternative_sources()
    for key, value in summary.items():
        if key in {"rows", "top_rows"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
