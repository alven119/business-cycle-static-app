#!/usr/bin/env python3
"""Show Phase82 replay/backtest lineage hardening closure summary."""

from __future__ import annotations

from business_cycle.audits.phase82_replay_backtest_lineage_closure import (
    summarize_phase82_replay_backtest_lineage_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase82_replay_backtest_lineage_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
