#!/usr/bin/env python
"""Show Phase102 guided DS925+ install/read-only smoke summary."""

from __future__ import annotations

from business_cycle.service.nas_guided_ds925_install_smoke import (
    summarize_nas_guided_ds925_install_smoke,
)


def main() -> int:
    summary = summarize_nas_guided_ds925_install_smoke()
    for key, value in summary.items():
        if key == "nas_guided_ds925_install_smoke":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
