#!/usr/bin/env python
"""Show Phase 40 current-data refresh audit."""

from __future__ import annotations

from business_cycle.audits.phase40_current_data_refresh import (
    summarize_phase40_current_data_refresh,
)


def main() -> int:
    summary = summarize_phase40_current_data_refresh()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
