#!/usr/bin/env python
"""Show Phase 119 strict replay input timeline contract."""

from business_cycle.storage.nas_strict_replay_input_timeline import (
    summarize_nas_strict_replay_input_timeline_contract,
)


def main() -> int:
    summary = summarize_nas_strict_replay_input_timeline_contract()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
