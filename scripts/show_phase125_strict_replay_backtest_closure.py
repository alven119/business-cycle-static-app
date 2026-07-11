#!/usr/bin/env python
"""Show Phase 125 closure fields."""

from business_cycle.audits.phase125_strict_replay_backtest_closure import (
    summarize_phase125_strict_replay_backtest_closure,
)


def main() -> int:
    summary = summarize_phase125_strict_replay_backtest_closure()
    for key, value in summary.items():
        if key == "artifact":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
