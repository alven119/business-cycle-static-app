#!/usr/bin/env python
"""Show Phase62 indicator dashboard explanation drill-down readiness."""

from __future__ import annotations

from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    summarize_indicator_dashboard_explanation_drilldown,
)


def main() -> int:
    summary = summarize_indicator_dashboard_explanation_drilldown()
    for key, value in summary.items():
        if key == "drilldown_artifact":
            continue
        print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
