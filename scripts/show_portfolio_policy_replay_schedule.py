#!/usr/bin/env python3
"""Show Phase77 portfolio policy replay schedule contract summary."""

from __future__ import annotations

from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)


def main() -> int:
    """Print key=value summary lines for CI and phase reports."""

    summary = summarize_portfolio_policy_replay_schedule()
    for key, value in summary.items():
        if key in {"scheduled_template_ids", "schedule_families"}:
            print(f"{key}={','.join(value)}")
        else:
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
