#!/usr/bin/env python
"""Show Phase107 NAS app container runtime bundle closure."""

from __future__ import annotations

from business_cycle.audits.phase107_nas_app_container_runtime_bundle_closure import (
    summarize_phase107_nas_app_container_runtime_bundle_closure,
)


def main() -> int:
    summary = summarize_phase107_nas_app_container_runtime_bundle_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
