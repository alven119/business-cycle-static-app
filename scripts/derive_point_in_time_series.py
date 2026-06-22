#!/usr/bin/env python
"""Derive feature-gated point-in-time series from strict input snapshots."""

from __future__ import annotations

import argparse

from business_cycle.audits.point_in_time_coverage import scenario_month_end_dates
from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.indicators.point_in_time_derived import derive_rrsfs_snapshot
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series-id", required=True, choices=["RRSFS"])
    parser.add_argument("--as-of")
    parser.add_argument("--scenario-horizons", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    as_of_dates = [args.as_of] if args.as_of else []
    if args.scenario_horizons:
        as_of_dates = scenario_month_end_dates("specs/backtests/scenarios.yaml")
    cache = PointInTimeCache(args.cache_dir)
    derived = 0
    missing = 0
    last_error = "none"
    for as_of in as_of_dates:
        try:
            value = derive_rrsfs_as_of(cache=cache, as_of=as_of)
        except (PointInTimeError, PointInTimeCacheError) as exc:
            missing += 1
            last_error = str(exc)
            continue
        derived += 1
        if not args.scenario_horizons:
            print(f"series_id={value.series_id}")
            print(f"as_of={value.as_of}")
            print(f"selected_reference_month={value.selected_reference_month}")
            print(f"value={round(value.value, 6)}")
            print(f"formula_id={value.formula_id}")
            print(f"formula_version={value.formula_version}")
            print(f"input_snapshot_ids={','.join(value.input_snapshot_ids)}")
            print(f"availability_date={value.availability_date}")
            print(f"temporal_evidence_class={value.temporal_evidence_class}")
            print(f"point_in_time={str(value.point_in_time).lower()}")
            print(f"revised_fallback={str(value.revised_fallback).lower()}")
    total = len(as_of_dates)
    print(f"requested_series_id={args.series_id}")
    print(f"requested_as_of_count={total}")
    print(f"rrsfs_derived_snapshot_count={derived}")
    print(f"rrsfs_missing_pair_count={missing}")
    print(f"rrsfs_required_horizon_coverage_ratio={0.0 if total == 0 else round(derived / total, 6)}")
    print("rrsfs_formula_validated=false")
    print("rrsfs_unit_validated=false")
    print("rrsfs_base_period_validated=false")
    print("rrsfs_seasonal_adjustment_validated=false")
    print("rrsfs_same_as_of_rule_validated=true")
    print("rrsfs_strict_ready=false")
    print("revised_default_unchanged=true")
    print(f"last_missing_reason={last_error}")
    print("result=blocked")
    return 0


def derive_rrsfs_as_of(*, cache: PointInTimeCache, as_of: str):
    rsafs = cache.read_series("RSAFS")
    cpi = cache.read_series("CPIAUCSL")
    rsafs_snapshot = select_vintage_as_of(rsafs.rows, series_id="RSAFS", as_of=as_of)
    cpi_snapshot = select_vintage_as_of(cpi.rows, series_id="CPIAUCSL", as_of=as_of)
    return derive_rrsfs_snapshot(
        as_of=as_of,
        rsafs_snapshot=rsafs_snapshot,
        cpi_snapshot=cpi_snapshot,
    )


if __name__ == "__main__":
    raise SystemExit(main())
