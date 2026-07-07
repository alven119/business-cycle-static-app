#!/usr/bin/env python3
"""Show Phase89A portfolio policy wording alignment closure."""

from __future__ import annotations

from business_cycle.audits.phase89a_portfolio_policy_wording_alignment_closure import (
    summarize_phase89a_portfolio_policy_wording_alignment_closure,
)


def main() -> int:
    summary = summarize_phase89a_portfolio_policy_wording_alignment_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            print(f"{key}=<rows:{len(value)}>")
        else:
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
