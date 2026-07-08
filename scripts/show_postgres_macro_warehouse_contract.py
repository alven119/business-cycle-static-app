#!/usr/bin/env python
"""Show Phase 91 Postgres macro warehouse contract readiness."""

from __future__ import annotations

from business_cycle.storage.postgres_macro_warehouse import (
    summarize_postgres_macro_warehouse_contract,
)


def main() -> int:
    summary = summarize_postgres_macro_warehouse_contract()
    for key, value in summary.items():
        if key == "schema_sql_preview":
            continue
        if isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
