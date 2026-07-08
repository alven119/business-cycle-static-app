#!/usr/bin/env python
"""Generate a Phase 93 vintage/PIT backfill availability dry-run artifact."""

from __future__ import annotations

import argparse

from business_cycle.storage.vintage_pit_backfill_availability import (
    build_vintage_pit_backfill_availability_manifest,
    write_vintage_pit_backfill_availability_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest = build_vintage_pit_backfill_availability_manifest()
    result = write_vintage_pit_backfill_availability_manifest(
        manifest,
        output=args.output,
    )
    for key, value in {
        "vintage_pit_backfill_accounting_ready": manifest[
            "vintage_pit_backfill_accounting_ready"
        ],
        "role_with_pit_backfill_plan_count": manifest[
            "role_with_pit_backfill_plan_count"
        ],
        "planned_vintage_request_row_count": manifest[
            "planned_vintage_request_row_count"
        ],
        "observation_vintage_row_count": manifest["observation_vintage_row_count"],
        "output": result["output"],
    }.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
