#!/usr/bin/env python
"""Show Phase107 NAS app container runtime bundle readiness."""

from __future__ import annotations

from business_cycle.service.nas_app_container_runtime_bundle import (
    summarize_nas_app_container_runtime_bundle,
)


def main() -> int:
    summary = summarize_nas_app_container_runtime_bundle()
    for key, value in summary.items():
        if key == "nas_app_container_runtime_bundle":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
