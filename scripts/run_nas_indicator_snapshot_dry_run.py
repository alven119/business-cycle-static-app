#!/usr/bin/env python
"""Generate a Phase 94 NAS indicator snapshot dry-run artifact."""

from __future__ import annotations

import argparse

from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
    write_nas_indicator_snapshot_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest = build_nas_indicator_snapshot_manifest()
    result = write_nas_indicator_snapshot_manifest(manifest, output=args.output)
    for key, value in {
        "nas_indicator_snapshot_materialization_ready": manifest[
            "nas_indicator_snapshot_materialization_ready"
        ],
        "role_snapshot_count": manifest["role_snapshot_count"],
        "series_snapshot_count": manifest["series_snapshot_count"],
        "service_view_model_ready": manifest["service_view_model_ready"],
        "output": result["output"],
    }.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
