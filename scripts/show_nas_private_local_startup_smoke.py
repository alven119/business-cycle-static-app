#!/usr/bin/env python
"""Show Phase101 private local startup smoke summary."""

from __future__ import annotations

from business_cycle.service.nas_private_local_startup_smoke import (
    summarize_nas_private_local_startup_smoke,
)


def main() -> int:
    summary = summarize_nas_private_local_startup_smoke()
    for key, value in summary.items():
        if key == "nas_private_local_startup_smoke":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
