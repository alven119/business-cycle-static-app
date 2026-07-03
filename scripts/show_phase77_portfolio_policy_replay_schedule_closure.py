#!/usr/bin/env python3
"""Show Phase77 portfolio replay schedule closure summary."""

from __future__ import annotations

from business_cycle.audits.phase77_portfolio_policy_replay_schedule_closure import (
    summarize_phase77_portfolio_policy_replay_schedule_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase77_portfolio_policy_replay_schedule_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
