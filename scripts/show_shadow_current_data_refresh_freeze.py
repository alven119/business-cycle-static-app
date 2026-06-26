#!/usr/bin/env python
"""Show Phase 40 alpha37 current-data refresh freeze."""

from __future__ import annotations

from business_cycle.audits.shadow_current_data_refresh_freeze import (
    summarize_shadow_current_data_refresh_freeze,
)


def main() -> int:
    summary = summarize_shadow_current_data_refresh_freeze()
    for key, value in summary.items():
        if key in {"source_file_hashes", "parent_freeze", "audit"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["current_data_refresh_freeze_ready"] else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
