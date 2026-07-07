#!/usr/bin/env python3
"""Show Phase88 portfolio policy replay research surface closure."""

from __future__ import annotations

from business_cycle.audits.phase88_portfolio_policy_replay_research_surface_closure import (
    summarize_phase88_portfolio_policy_replay_research_surface_closure,
)


def main() -> int:
    summary = summarize_phase88_portfolio_policy_replay_research_surface_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            print(f"{key}=<rows:{len(value)}>")
        else:
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
