#!/usr/bin/env python
"""Show Phase103 DS925+ connectivity smoke closure."""

from __future__ import annotations

from business_cycle.audits.phase103_ds925_connectivity_smoke_closure import (
    summarize_phase103_ds925_connectivity_smoke_closure,
)


def main() -> int:
    summary = summarize_phase103_ds925_connectivity_smoke_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
