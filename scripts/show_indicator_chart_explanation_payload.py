#!/usr/bin/env python
"""Show Phase64 indicator chart payload readiness."""

from __future__ import annotations

from business_cycle.render.indicator_chart_explanation_payload import (
    summarize_indicator_chart_explanation_payload,
)


def main() -> int:
    summary = summarize_indicator_chart_explanation_payload()
    for key, value in summary.items():
        if key == "chart_payload_artifact":
            continue
        print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
