#!/usr/bin/env python3
"""Show Phase79 historical replay runner preview summary."""

from __future__ import annotations

from business_cycle.validation.historical_replay_runner import (
    summarize_historical_replay_runner_preview,
)


def main() -> int:
    """Print key=value summary lines for CI and phase reports."""

    summary = summarize_historical_replay_runner_preview()
    for key, value in summary.items():
        if key == "replay_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
