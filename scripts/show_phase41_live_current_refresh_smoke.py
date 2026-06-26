#!/usr/bin/env python
"""Show Phase 41 live/current refresh smoke audit."""

from __future__ import annotations

from dotenv import load_dotenv

from business_cycle.audits.phase41_live_current_refresh_smoke import (
    summarize_phase41_live_current_refresh_smoke,
)


def main() -> int:
    load_dotenv()
    summary = summarize_phase41_live_current_refresh_smoke()
    for key, value in summary.items():
        if key in {
            "source",
            "probe",
            "manifest",
            "stale",
            "snapshot",
            "dashboard",
            "browser_verification",
        }:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
