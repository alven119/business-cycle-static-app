#!/usr/bin/env python
"""Show Phase106 NAS operator live deployment session protocol readiness."""

from __future__ import annotations

from business_cycle.service.nas_operator_live_deployment_session import (
    summarize_nas_operator_live_deployment_session,
)


def main() -> int:
    summary = summarize_nas_operator_live_deployment_session()
    for key, value in summary.items():
        if key == "nas_operator_live_deployment_session":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
