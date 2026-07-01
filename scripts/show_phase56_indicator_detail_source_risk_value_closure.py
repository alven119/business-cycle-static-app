#!/usr/bin/env python
"""Show Phase56 closure."""

from __future__ import annotations

from business_cycle.audits.phase56_indicator_detail_source_risk_value_closure import (
    summarize_phase56_indicator_detail_source_risk_value_closure,
)


def main() -> int:
    summary = summarize_phase56_indicator_detail_source_risk_value_closure()
    for key, value in summary.items():
        if key in {
            "indicator_detail_source_risk_value_summary",
            "product_capability_progress_summary",
            "product_capability_95_roadmap_summary",
            "product_capability_progress",
        }:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
