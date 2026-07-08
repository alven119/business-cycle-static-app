#!/usr/bin/env python
"""Generate a Phase 92 revised macro data import dry-run artifact."""

from __future__ import annotations

import argparse

from business_cycle.storage.revised_macro_data_import import (
    build_revised_macro_data_import_manifest,
    write_revised_macro_data_import_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--cache-dir")
    parser.add_argument("--snapshot-as-of", default="2026-07-03")
    parser.add_argument("--no-tmp-seed", action="store_true")
    args = parser.parse_args()

    manifest = build_revised_macro_data_import_manifest(
        cache_dir=args.cache_dir,
        seed_tmp_cache_when_missing=not args.no_tmp_seed,
        snapshot_as_of=args.snapshot_as_of,
    )
    result = write_revised_macro_data_import_manifest(manifest, output=args.output)
    for key, value in {
        "revised_macro_data_import_dry_run_ready": manifest[
            "revised_macro_data_import_dry_run_ready"
        ],
        "role_count": manifest["role_count"],
        "revised_import_ready_role_count": manifest[
            "revised_import_ready_role_count"
        ],
        "observation_revised_row_count": manifest["observation_revised_row_count"],
        "output": result["output"],
    }.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
