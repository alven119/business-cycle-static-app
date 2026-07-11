#!/usr/bin/env python
"""Show Phase 118 broader PIT, calendar, and replay-input contract."""

from business_cycle.storage.nas_broader_pit_release_replay import (
    summarize_nas_broader_pit_release_replay_contract,
)


def main() -> int:
    summary = summarize_nas_broader_pit_release_replay_contract()
    for key, value in summary.items():
        if key != "revision_aware_release_calendar_plan":
            rendered = str(value).lower() if isinstance(value, bool) else value
            print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
