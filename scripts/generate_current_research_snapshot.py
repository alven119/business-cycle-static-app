#!/usr/bin/env python
"""Generate a Phase 39 current research snapshot artifact."""

from __future__ import annotations

import argparse

from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    summarize_current_research_snapshot,
    write_current_research_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    snapshot = build_current_research_snapshot()
    write = write_current_research_snapshot(snapshot, output=args.output)
    summary = summarize_current_research_snapshot()
    for key, value in summary.items():
        if key == "snapshot":
            continue
        print(f"{key}={_format_value(value)}")
    print(f"output={write['output']}")
    print(
        "result="
        f"{'passed' if summary['current_research_snapshot_runtime_ready'] else 'blocked'}"
    )
    return 0 if summary["current_research_snapshot_runtime_ready"] else 1


def _format_value(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
