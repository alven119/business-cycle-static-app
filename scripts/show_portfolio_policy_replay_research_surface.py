#!/usr/bin/env python3
"""Show Phase88 portfolio policy replay research surface readiness."""

from __future__ import annotations

from business_cycle.render.portfolio_policy_replay_research_surface import (
    summarize_portfolio_policy_replay_research_surface,
)


def main() -> int:
    summary = summarize_portfolio_policy_replay_research_surface()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
