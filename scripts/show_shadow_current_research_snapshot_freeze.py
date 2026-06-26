#!/usr/bin/env python
"""Show Phase 39 alpha36 current research snapshot freeze."""

from __future__ import annotations

from business_cycle.audits.shadow_current_research_snapshot_freeze import (
    summarize_shadow_current_research_snapshot_freeze,
)


def main() -> None:
    summary = summarize_shadow_current_research_snapshot_freeze()
    for key, value in summary.items():
        if key in {"source_file_hashes", "parent_freeze", "audit"}:
            continue
        print(f"{key}={_format_value(value)}")


def _format_value(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    main()
