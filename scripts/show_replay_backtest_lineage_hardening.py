#!/usr/bin/env python3
"""Show Phase82 replay/backtest lineage hardening summary."""

from __future__ import annotations

from business_cycle.portfolio.replay_backtest_lineage_hardening import (
    build_replay_backtest_lineage_hardening_report,
)


def main() -> int:
    """Print key=value lineage hardening lines."""

    summary = build_replay_backtest_lineage_hardening_report()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
