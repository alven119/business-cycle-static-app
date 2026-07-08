#!/usr/bin/env python
"""Show Phase 90 NAS dynamic-service architecture closure."""

from __future__ import annotations

from business_cycle.audits.phase90_nas_dynamic_service_architecture_closure import (
    summarize_phase90_nas_dynamic_service_architecture_closure,
)


def main() -> int:
    summary = summarize_phase90_nas_dynamic_service_architecture_closure()
    for key, value in summary.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
