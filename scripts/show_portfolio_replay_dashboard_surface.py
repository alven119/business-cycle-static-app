#!/usr/bin/env python3
"""Show Phase81 portfolio/replay dashboard surface summary."""

from __future__ import annotations

from business_cycle.render.portfolio_replay_dashboard_surface import (
    summarize_portfolio_replay_dashboard_surface,
)


def main() -> int:
    """Print key=value summary lines."""

    summary = summarize_portfolio_replay_dashboard_surface()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
