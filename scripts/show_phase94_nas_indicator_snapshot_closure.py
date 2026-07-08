#!/usr/bin/env python
"""Show Phase 94 NAS indicator snapshot materialization closure."""

from __future__ import annotations

from business_cycle.audits.phase94_nas_indicator_snapshot_closure import (
    summarize_phase94_nas_indicator_snapshot_closure,
)


def main() -> int:
    summary = summarize_phase94_nas_indicator_snapshot_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
