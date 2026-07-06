#!/usr/bin/env python3
"""Show Phase78 cash-flow-aware backtest kernel contract summary."""

from __future__ import annotations

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)


def main() -> int:
    """Print key=value summary lines for CI and phase reports."""

    summary = summarize_cash_flow_backtest_kernel_contract()
    for key, value in summary.items():
        if key in {"component_ids", "fixture_ids"}:
            print(f"{key}={','.join(value)}")
        else:
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
