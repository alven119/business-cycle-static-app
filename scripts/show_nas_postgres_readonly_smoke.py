#!/usr/bin/env python
"""Show Phase99 NAS Postgres read-only smoke readiness."""

from __future__ import annotations

from business_cycle.storage.nas_postgres_readonly_smoke import (
    summarize_nas_postgres_readonly_smoke,
)


def main() -> int:
    summary = summarize_nas_postgres_readonly_smoke()
    for key, value in summary.items():
        if key == "nas_postgres_readonly_smoke":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
