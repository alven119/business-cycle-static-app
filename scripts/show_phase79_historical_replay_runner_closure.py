#!/usr/bin/env python3
"""Show Phase79 historical replay runner closure summary."""

from __future__ import annotations

from business_cycle.audits.phase79_historical_replay_runner_closure import (
    summarize_phase79_historical_replay_runner_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase79_historical_replay_runner_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
