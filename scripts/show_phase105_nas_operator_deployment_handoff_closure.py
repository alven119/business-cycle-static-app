#!/usr/bin/env python
"""Show Phase105 NAS operator deployment handoff closure."""

from __future__ import annotations

from business_cycle.audits.phase105_nas_operator_deployment_handoff_closure import (
    summarize_phase105_nas_operator_deployment_handoff_closure,
)


def main() -> int:
    summary = summarize_phase105_nas_operator_deployment_handoff_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
