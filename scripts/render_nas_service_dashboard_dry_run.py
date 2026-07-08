#!/usr/bin/env python
"""Render Phase95 NAS service dashboard rehearsal artifacts under /tmp."""

from __future__ import annotations

import argparse

from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    write_nas_service_dashboard_dry_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    bundle = build_nas_service_dashboard_bundle()
    result = write_nas_service_dashboard_dry_run(
        bundle,
        output_dir=args.output_dir,
    )
    print(
        "nas_service_dashboard_ready="
        f"{str(bundle['nas_service_dashboard_ready']).lower()}",
    )
    for key in (
        "dry_run_output_under_tmp_only",
        "written_file_count",
        "repo_output_written_count",
        "public_output_count",
    ):
        value = result[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    return 0 if bundle["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
