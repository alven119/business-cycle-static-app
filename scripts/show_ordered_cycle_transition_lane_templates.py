#!/usr/bin/env python
"""Show Phase58 full ordered-cycle transition lane template readiness."""

from __future__ import annotations

from business_cycle.render.ordered_cycle_transition_lane_templates import (
    summarize_full_ordered_cycle_transition_lane_templates,
)


def main() -> int:
    summary = summarize_full_ordered_cycle_transition_lane_templates()
    for key, value in summary.items():
        if key == "transition_lane_templates":
            continue
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
