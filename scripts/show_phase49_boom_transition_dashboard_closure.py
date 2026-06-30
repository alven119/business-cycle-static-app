#!/usr/bin/env python
"""Show Phase49 closure."""

from __future__ import annotations

from business_cycle.audits.phase49_boom_transition_dashboard_closure import (
    summarize_phase49_boom_transition_dashboard_closure,
)


def main() -> int:
    summary = summarize_phase49_boom_transition_dashboard_closure()
    for key, value in summary.items():
        if key in {"surface_summary", "dashboard_runtime"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
