#!/usr/bin/env python
"""Show Phase 133 closure."""

from business_cycle.audits.phase133_historical_transition_policy_timeline_closure import (
    summarize_phase133_historical_transition_policy_timeline_closure,
)


def main() -> int:
    summary = summarize_phase133_historical_transition_policy_timeline_closure()
    for key, value in summary.items():
        if key != "timeline":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
