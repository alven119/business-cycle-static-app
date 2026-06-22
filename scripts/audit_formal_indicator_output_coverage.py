#!/usr/bin/env python
"""Audit end-to-end formal indicator output coverage under strict PIT inputs."""

from __future__ import annotations

import argparse

from business_cycle.audits.formal_indicator_output_coverage import (
    summarize_formal_indicator_output_coverage,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-path", default="specs/indicator_catalog.yaml")
    parser.add_argument("--scenarios-path", default="specs/backtests/scenarios.yaml")
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = summarize_formal_indicator_output_coverage(
        catalog_path=args.catalog_path,
        scenarios_path=args.scenarios_path,
        cache_dir=args.cache_dir,
    )
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
