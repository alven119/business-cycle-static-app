#!/usr/bin/env python
"""Show Phase62 indicator dashboard explanation drill-down closure."""

from __future__ import annotations

from business_cycle.audits.phase62_indicator_dashboard_explanation_drilldown_closure import (
    summarize_phase62_indicator_dashboard_explanation_drilldown_closure,
)


def main() -> int:
    summary = summarize_phase62_indicator_dashboard_explanation_drilldown_closure()
    for key, value in summary.items():
        if key.endswith("_summary") or key == "product_capability_progress":
            continue
        print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
