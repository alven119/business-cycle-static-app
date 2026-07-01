#!/usr/bin/env python
"""Show Phase58 full ordered-cycle transition lane closure."""

from __future__ import annotations

from business_cycle.audits.phase58_ordered_cycle_transition_lane_templates_closure import (
    summarize_phase58_ordered_cycle_transition_lane_templates_closure,
)


def main() -> int:
    summary = summarize_phase58_ordered_cycle_transition_lane_templates_closure()
    for key, value in summary.items():
        if key.endswith("_summary") or key == "product_capability_progress":
            continue
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
