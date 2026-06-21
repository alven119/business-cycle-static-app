#!/usr/bin/env python
"""Audit formal series temporal/economic substitution equivalence."""

from __future__ import annotations

import argparse

from business_cycle.audits.temporal_equivalence import (
    summarize_formal_series_temporal_equivalence,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        default="specs/audits/formal_temporal_gap_remediation.yaml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = summarize_formal_series_temporal_equivalence(args.matrix)
    for key in (
        "remediation_series_count",
        "proposed_substitution_count",
        "temporally_equivalent_substitution_count",
        "economically_equivalent_substitution_count",
        "signal_equivalent_substitution_count",
        "approved_feature_gated_substitution_count",
        "silent_substitution_count",
        "rejected_substitution_count",
        "result",
    ):
        print(f"{key}={_format(summary[key])}")
    if summary["unresolved_formal_series_ids"]:
        print("unresolved_formal_series_ids=" + ",".join(summary["unresolved_formal_series_ids"]))
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
