#!/usr/bin/env python
"""Show Phase 94 NAS indicator snapshot materialization readiness."""

from __future__ import annotations

from business_cycle.storage.nas_indicator_snapshots import (
    summarize_nas_indicator_snapshot,
)


def main() -> int:
    summary = summarize_nas_indicator_snapshot()
    for key, value in summary.items():
        if key == "nas_indicator_snapshot_manifest":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
