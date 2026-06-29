#!/usr/bin/env python
"""Show Phase48 boom transition evidence wiring summary."""

from __future__ import annotations

from business_cycle.transition_monitor.boom_evidence_wiring import (
    build_boom_transition_evidence_wiring,
)


def main() -> int:
    summary = build_boom_transition_evidence_wiring()
    for key, value in summary.items():
        if key in {"priority_role_rows", "priority_lane_rows", "lane_coverage"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
