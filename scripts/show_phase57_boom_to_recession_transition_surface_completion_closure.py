#!/usr/bin/env python
"""Show Phase57 boom-to-recession transition surface completion closure."""

from __future__ import annotations

from business_cycle.audits.phase57_boom_to_recession_transition_surface_completion_closure import (
    summarize_phase57_boom_to_recession_transition_surface_completion_closure,
)


def main() -> None:
    summary = summarize_phase57_boom_to_recession_transition_surface_completion_closure()
    for key, value in summary.items():
        if key.endswith("_summary") or key == "product_capability_progress":
            continue
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
