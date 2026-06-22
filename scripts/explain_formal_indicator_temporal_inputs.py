#!/usr/bin/env python
"""Explain temporal input provenance for formal indicator scoring."""

from __future__ import annotations

import argparse
import json
from typing import Any

from business_cycle.audits.formal_indicator_temporal_inputs import (
    explain_formal_indicator_temporal_inputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--catalog-path", default="specs/indicator_catalog.yaml")
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    parser.add_argument("--json", action="store_true", help="Print full JSON details.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = explain_formal_indicator_temporal_inputs(
        as_of=args.as_of,
        catalog_path=args.catalog_path,
        cache_dir=args.cache_dir,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    for key, value in summary.items():
        if key == "indicators":
            continue
        print(f"{key}={_format(value)}")
    for item in summary["indicators"]:
        print(
            "indicator "
            f"indicator_id={item['indicator_id']} "
            f"strict_output_ready={_format(item['strict_output_ready'])} "
            f"dependency_series_ids={','.join(item['dependency_series_ids'])} "
            f"direct_or_derived={item['direct_or_derived']} "
            f"temporal_evidence_class={item['temporal_evidence_class']} "
            f"source_artifact_ids={','.join(item['source_artifact_ids'])} "
            f"selected_observation_dates={','.join(item['selected_observation_dates'])} "
            f"availability_dates={','.join(item['availability_dates'])} "
            f"missing_dependencies={','.join(item['missing_dependencies'])} "
            f"proxy_used={_format(item['proxy_used'])} "
            f"revised_fallback_used={_format(item['revised_fallback_used'])}"
        )
    return 0


def _format(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
