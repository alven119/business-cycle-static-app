#!/usr/bin/env python
"""Show Phase 75 closure readiness."""

from __future__ import annotations

from business_cycle.audits.phase75_all_capability_roadmap_portfolio_research_closure import (
    summarize_phase75_all_capability_roadmap_portfolio_research_closure,
)


def main() -> int:
    summary = summarize_phase75_all_capability_roadmap_portfolio_research_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
