#!/usr/bin/env python
"""Show Phase 41 alpha38 live current refresh smoke freeze."""

from __future__ import annotations

from dotenv import load_dotenv

from business_cycle.audits.shadow_live_current_refresh_smoke_freeze import (
    summarize_shadow_live_current_refresh_smoke_freeze,
)


def main() -> int:
    load_dotenv()
    summary = summarize_shadow_live_current_refresh_smoke_freeze()
    for key, value in summary.items():
        if key in {"source_file_hashes", "parent_freeze", "audit"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["live_current_refresh_smoke_freeze_ready"] else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
