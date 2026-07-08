#!/usr/bin/env python
"""Show Phase105 NAS operator deployment handoff readiness."""

from __future__ import annotations

from business_cycle.service.nas_operator_deployment_handoff import (
    summarize_nas_operator_deployment_handoff,
)


def main() -> int:
    summary = summarize_nas_operator_deployment_handoff()
    for key, value in summary.items():
        if key == "nas_operator_deployment_handoff":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
