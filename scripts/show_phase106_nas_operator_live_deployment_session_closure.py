#!/usr/bin/env python
"""Show Phase106 NAS operator live deployment session closure."""

from __future__ import annotations

from business_cycle.audits.phase106_nas_operator_live_deployment_session_closure import (
    summarize_phase106_nas_operator_live_deployment_session_closure,
)


def main() -> int:
    summary = summarize_phase106_nas_operator_live_deployment_session_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
