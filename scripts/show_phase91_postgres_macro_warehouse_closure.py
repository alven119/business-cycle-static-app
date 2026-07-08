#!/usr/bin/env python
"""Show Phase 91 Postgres macro warehouse closure."""

from __future__ import annotations

from business_cycle.audits.phase91_postgres_macro_warehouse_closure import (
    summarize_phase91_postgres_macro_warehouse_closure,
)


def main() -> int:
    summary = summarize_phase91_postgres_macro_warehouse_closure()
    for key, value in summary.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
