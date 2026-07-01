#!/usr/bin/env python
"""Show Phase53 closure."""

from __future__ import annotations

from business_cycle.audits.phase53_composite_transition_surface_value_wiring_closure import (
    summarize_phase53_composite_transition_surface_value_wiring_closure,
)


def main() -> int:
    summary = summarize_phase53_composite_transition_surface_value_wiring_closure()
    for key, value in summary.items():
        if key in {
            "value_wiring_summary",
            "boom_transition_surface_summary",
            "product_capability_progress_summary",
            "product_capability_progress",
        }:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
