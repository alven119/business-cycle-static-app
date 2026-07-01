#!/usr/bin/env python
"""Show Phase55 macro indicator coverage readiness matrix."""

from __future__ import annotations

from business_cycle.audits.macro_indicator_coverage_readiness_matrix import (
    summarize_macro_indicator_coverage_readiness_matrix,
)


def main() -> int:
    summary = summarize_macro_indicator_coverage_readiness_matrix()
    for key, value in summary.items():
        if key in {"rows", "dashboard_view_model"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
