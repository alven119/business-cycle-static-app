#!/usr/bin/env python
"""Show the Phase 120 command-center rehearsal summary."""

from business_cycle.render.nas_cycle_command_center import (
    summarize_nas_cycle_command_center,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
)


def main() -> int:
    summary = summarize_nas_cycle_command_center(
        build_nas_indicator_snapshot_manifest()
    )
    for key, value in summary.items():
        if key == "command_center":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
