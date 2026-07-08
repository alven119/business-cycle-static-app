#!/usr/bin/env python
"""Run Phase99 fixture-backed NAS Postgres read-only smoke."""

from __future__ import annotations

from business_cycle.storage.nas_postgres_readonly_smoke import (
    build_nas_postgres_readonly_smoke,
)


def main() -> int:
    smoke = build_nas_postgres_readonly_smoke()
    for key in (
        "nas_postgres_readonly_smoke_ready",
        "readonly_query_pass_count",
        "readonly_result_row_count",
        "forbidden_sql_rejected_count",
        "forbidden_sql_accepted_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "runtime_dependency_added_count",
        "public_output_count",
    ):
        value = smoke[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    return 0 if smoke["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
