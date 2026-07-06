#!/usr/bin/env python3
"""Show Phase78 cash-flow-aware backtest kernel closure summary."""

from __future__ import annotations

from business_cycle.audits.phase78_cash_flow_backtest_kernel_closure import (
    summarize_phase78_cash_flow_backtest_kernel_closure,
)


def main() -> int:
    """Print key=value closure lines."""

    summary = summarize_phase78_cash_flow_backtest_kernel_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
