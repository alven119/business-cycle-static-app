#!/usr/bin/env python3
"""Show Phase83 indicator trend drilldown closure summary."""

from __future__ import annotations

from business_cycle.audits.phase83_indicator_trend_drilldown_closure import (
    summarize_phase83_indicator_trend_drilldown_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase83_indicator_trend_drilldown_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
