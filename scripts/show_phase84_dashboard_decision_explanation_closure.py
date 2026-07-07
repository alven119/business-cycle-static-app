#!/usr/bin/env python3
"""Show Phase84 dashboard decision explanation closure summary."""

from __future__ import annotations

from business_cycle.audits.phase84_dashboard_decision_explanation_closure import (
    summarize_phase84_dashboard_decision_explanation_closure,
)


def main() -> int:
    summary = summarize_phase84_dashboard_decision_explanation_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
