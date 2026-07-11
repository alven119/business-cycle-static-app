#!/usr/bin/env python
"""Show Phase 118 broader PIT and strict replay input closure."""

from business_cycle.audits.phase118_broader_pit_release_replay_closure import (
    summarize_phase118_broader_pit_release_replay_closure,
)


def main() -> int:
    summary = summarize_phase118_broader_pit_release_replay_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
