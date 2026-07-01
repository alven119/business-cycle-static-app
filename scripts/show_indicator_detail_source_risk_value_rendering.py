#!/usr/bin/env python
"""Show Phase56 indicator detail source-risk value rendering."""

from __future__ import annotations

from business_cycle.render.indicator_detail_source_risk_values import (
    summarize_indicator_detail_source_risk_value_rendering,
)


def main() -> int:
    summary = summarize_indicator_detail_source_risk_value_rendering()
    for key, value in summary.items():
        if key in {"cards", "dashboard_view_model"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
