#!/usr/bin/env python
"""Show the canonical scenario/as-of inventory used by temporal audits."""

from __future__ import annotations

import argparse

from business_cycle.audits.scenario_as_of_inventory import (
    load_canonical_scenario_as_of_inventory,
    summarize_scenario_as_of_inventory,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios-path", default="specs/backtests/scenarios.yaml")
    parser.add_argument("--show-differences", action="store_true")
    parser.add_argument("--max-rows", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = summarize_scenario_as_of_inventory(args.scenarios_path)
    for key, value in summary.items():
        if isinstance(value, list):
            continue
        print(f"{key}={_format(value)}")
    if args.show_differences:
        entries = load_canonical_scenario_as_of_inventory(args.scenarios_path)
        for entry in entries[: args.max_rows]:
            print(
                "scenario_as_of "
                f"scenario_id={entry.scenario_id} as_of={entry.as_of} "
                f"included_in_leaf_temporal_audit={_format(entry.included_in_leaf_temporal_audit)} "
                "included_in_formal_indicator_output_audit="
                f"{_format(entry.included_in_formal_indicator_output_audit)}"
            )
    return 0 if summary["scenario_as_of_universe_consistent"] else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
