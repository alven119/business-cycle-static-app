#!/usr/bin/env python
"""Show Phase102 guided DS925+ install/read-only smoke closure."""

from __future__ import annotations

from business_cycle.audits.phase102_guided_ds925_install_smoke_closure import (
    summarize_phase102_guided_ds925_install_smoke_closure,
)


def main() -> int:
    summary = summarize_phase102_guided_ds925_install_smoke_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
