#!/usr/bin/env python3
"""Show Phase129 governed cycle transition closure."""

from business_cycle.audits.phase129_governed_cycle_transition_closure import (
    summarize_phase129_governed_cycle_transition_closure,
)


def main() -> None:
    summary = summarize_phase129_governed_cycle_transition_closure()
    for key, value in summary.items():
        if not isinstance(value, (dict, list)):
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
