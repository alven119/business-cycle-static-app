#!/usr/bin/env python
"""Write Phase107 NAS app container runtime bundle artifacts under /tmp."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_app_container_runtime_bundle import (
    write_nas_app_container_runtime_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    result = write_nas_app_container_runtime_bundle(args.output_dir)
    for key, value in result.items():
        if key == "written_paths":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if result["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
