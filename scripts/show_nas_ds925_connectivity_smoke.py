#!/usr/bin/env python
"""Show Phase103 DS925+ private-LAN connectivity smoke status."""

from __future__ import annotations

from business_cycle.service.nas_ds925_connectivity_smoke import (
    summarize_nas_ds925_connectivity_smoke,
)


def main() -> int:
    summary = summarize_nas_ds925_connectivity_smoke()
    for key, value in summary.items():
        if key == "nas_ds925_connectivity_smoke":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
