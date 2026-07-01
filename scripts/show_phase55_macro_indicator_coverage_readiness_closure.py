#!/usr/bin/env python
"""Show Phase55 closure."""

from __future__ import annotations

from business_cycle.audits.phase55_macro_indicator_coverage_readiness_closure import (
    summarize_phase55_macro_indicator_coverage_readiness_closure,
)


def main() -> int:
    summary = summarize_phase55_macro_indicator_coverage_readiness_closure()
    for key, value in summary.items():
        if key in {
            "macro_indicator_coverage_readiness_summary",
            "product_capability_progress_summary",
            "product_capability_progress",
        }:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
