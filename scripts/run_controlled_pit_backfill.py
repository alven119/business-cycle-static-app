#!/usr/bin/env python
"""Run Phase 37 controlled PIT backfill planning."""

from __future__ import annotations

import argparse

from business_cycle.validation.controlled_pit_backfill import (
    build_controlled_pit_backfill_plan,
    summarize_controlled_pit_backfill,
    write_controlled_pit_backfill,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run = build_controlled_pit_backfill_plan()
    write = write_controlled_pit_backfill(run, output=args.output)
    summary = summarize_controlled_pit_backfill()
    for key, value in summary.items():
        if key == "backfill_rows":
            continue
        print(f"{key}={value}")
    print(f"output={write['output']}")
    print(f"result={'passed' if run['controlled_pit_backfill_ready'] else 'blocked'}")
    return 0 if run["controlled_pit_backfill_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
