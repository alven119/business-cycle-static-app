#!/usr/bin/env python
"""Show Phase50 closure."""

from __future__ import annotations

from business_cycle.audits.phase50_transition_surface_data_risk_closure import (
    summarize_phase50_transition_surface_data_risk_closure,
)


def main() -> int:
    summary = summarize_phase50_transition_surface_data_risk_closure()
    for key, value in summary.items():
        if key == "phase49_summary":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
