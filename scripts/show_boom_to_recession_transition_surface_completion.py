#!/usr/bin/env python
"""Show Phase57 boom-to-recession transition surface completion summary."""

from __future__ import annotations

from business_cycle.render.boom_to_recession_transition_surface import (
    summarize_boom_to_recession_transition_surface_completion,
)


def main() -> None:
    summary = summarize_boom_to_recession_transition_surface_completion()
    for key, value in summary.items():
        if key == "transition_surface_completion":
            continue
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
