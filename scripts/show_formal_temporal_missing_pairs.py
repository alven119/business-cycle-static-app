#!/usr/bin/env python
"""Show missing strict PIT pairs for one formal leaf series."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series-id", required=True)
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    parser.add_argument("--scenarios-path", default="specs/backtests/scenarios.yaml")
    parser.add_argument("--max-pairs", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    series_id = args.series_id.strip().upper()
    pairs = _scenario_pairs(args.scenarios_path)
    cache = PointInTimeCache(args.cache_dir)
    missing: list[tuple[str, str, str]] = []
    covered = 0
    try:
        cached = cache.read_series(series_id)
    except PointInTimeCacheError:
        missing = [(scenario_id, as_of, "missing_authoritative_cache") for scenario_id, as_of in pairs]
    else:
        for scenario_id, as_of in pairs:
            try:
                snapshot = select_vintage_as_of(cached.rows, series_id=series_id, as_of=as_of)
            except PointInTimeError as exc:
                missing.append((scenario_id, as_of, str(exc)))
                continue
            if snapshot.observations:
                covered += 1
            else:
                missing.append((scenario_id, as_of, "no_legal_as_of_snapshot"))
    print(f"series_id={series_id}")
    print(f"required_pair_count={len(pairs)}")
    print(f"covered_pair_count={covered}")
    print(f"missing_pair_count={len(missing)}")
    print(f"required_reference_month_count={len({_reference_month(as_of) for _, as_of, _ in missing})}")
    print(f"required_release_date_range_start={missing[0][1] if missing else None}")
    print(f"required_release_date_range_end={missing[-1][1] if missing else None}")
    print("result=" + ("passed" if not missing else "blocked"))
    for scenario_id, as_of, reason in missing[: args.max_pairs]:
        print(
            "missing_pair "
            f"series_id={series_id} scenario_id={scenario_id} as_of={as_of} "
            f"reference_month={_reference_month(as_of)} missing_reason={reason}"
        )
    return 0


def _scenario_pairs(path: str | Path) -> list[tuple[str, str]]:
    import pandas as pd

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = []
    for scenario in payload.get("scenarios", []):
        scenario_id = str(scenario["scenario_id"])
        start = pd.Timestamp(str(scenario["window_start"]))
        end = pd.Timestamp(str(scenario["window_end"]))
        for timestamp in pd.date_range(start=start, end=end, freq="ME"):
            pairs.append((scenario_id, timestamp.date().isoformat()))
    return pairs


def _reference_month(as_of: str) -> str:
    year, month, _day = as_of.split("-")
    return f"{year}-{month}"


if __name__ == "__main__":
    raise SystemExit(main())
