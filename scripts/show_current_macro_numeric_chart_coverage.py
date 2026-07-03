#!/usr/bin/env python
"""Show Phase72 current macro numeric/chart coverage."""

from __future__ import annotations

from business_cycle.render.current_macro_numeric_chart_coverage import (
    summarize_current_macro_numeric_chart_coverage,
)


def main() -> int:
    summary = summarize_current_macro_numeric_chart_coverage()
    for key, value in summary.items():
        if key == "chart_coverage_artifact":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
