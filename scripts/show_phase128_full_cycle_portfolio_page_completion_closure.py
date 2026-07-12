#!/usr/bin/env python
"""Show Phase 128 full-cycle portfolio and page-completeness closure."""

from business_cycle.audits.phase128_full_cycle_portfolio_page_completion_closure import (
    summarize_phase128_full_cycle_portfolio_page_completion_closure,
)


def main() -> int:
    summary = summarize_phase128_full_cycle_portfolio_page_completion_closure()
    for key, value in summary.items():
        if key != "page_rows":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    for row in summary["page_rows"]:
        print(f"page.{row['route']}={row['page_status']}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
