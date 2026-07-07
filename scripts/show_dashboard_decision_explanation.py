#!/usr/bin/env python3
"""Show Phase84 dashboard decision explanation summary."""

from __future__ import annotations

from business_cycle.render.dashboard_decision_explanation import (
    summarize_dashboard_decision_explanation,
)


def main() -> int:
    summary = summarize_dashboard_decision_explanation()
    for key, value in summary.items():
        if key == "view_model":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
