#!/usr/bin/env python3
"""Show Phase80 research-only backtest artifact summary."""

from __future__ import annotations

from business_cycle.portfolio.research_backtest_artifacts import (
    summarize_research_backtest_artifacts,
)


def main() -> int:
    """Print key=value summary lines."""

    summary = summarize_research_backtest_artifacts()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
