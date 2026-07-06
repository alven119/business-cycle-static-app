#!/usr/bin/env python3
"""Show Phase81 portfolio/replay dashboard surface closure summary."""

from __future__ import annotations

from business_cycle.audits.phase81_portfolio_replay_dashboard_surface_closure import (
    summarize_phase81_portfolio_replay_dashboard_surface_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase81_portfolio_replay_dashboard_surface_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
