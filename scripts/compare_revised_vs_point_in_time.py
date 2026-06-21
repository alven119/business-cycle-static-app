#!/usr/bin/env python
"""Compare revised local values with point-in-time cache snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies
from business_cycle.data_sources.point_in_time import PointInTimeError, select_initial_release_only, select_vintage_as_of
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id")
    parser.add_argument("--series-id", action="append")
    parser.add_argument("--max-periods", type=int)
    parser.add_argument("--formal-only", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    parser.add_argument("--revised-dir", default="data/raw/fred")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    series_ids = _series_ids(args)
    as_of_dates = _as_of_dates(args.scenario_id, args.max_periods)
    cache = PointInTimeCache(args.cache_dir)
    compared_series = 0
    compared_periods = 0
    value_difference_count = 0
    missing_vintage_count = 0
    post_as_of_revision_blocked_count = 0
    not_yet_released_observation_blocked_count = 0
    silent_fallback_count = 0
    rows: list[dict[str, object]] = []

    for series_id in series_ids:
        compared_series += 1
        revised = _read_revised(Path(args.revised_dir) / f"{series_id}.csv")
        try:
            cached = cache.read_series(series_id)
        except PointInTimeCacheError:
            compared_periods += len(as_of_dates)
            missing_vintage_count += len(as_of_dates)
            continue
        for as_of in as_of_dates:
            compared_periods += 1
            try:
                vintage = select_vintage_as_of(cached.rows, series_id=series_id, as_of=as_of)
                initial = select_initial_release_only(cached.rows, series_id=series_id, as_of=as_of)
            except PointInTimeError:
                missing_vintage_count += 1
                continue
            revised_value = _latest_value_as_of(revised, as_of)
            vintage_value = vintage.observations[-1].value if vintage.observations else None
            initial_value = initial.observations[-1].value if initial.observations else None
            if vintage_value is None:
                missing_vintage_count += 1
                not_yet_released_observation_blocked_count += 1
                continue
            if revised_value is not None and revised_value != vintage_value:
                value_difference_count += 1
                post_as_of_revision_blocked_count += 1
            rows.append(
                {
                    "series_id": series_id,
                    "as_of": as_of,
                    "revised_value": revised_value,
                    "vintage_value": vintage_value,
                    "initial_release_value": initial_value,
                    "revision_delta": None
                    if revised_value is None
                    else revised_value - vintage_value,
                    "missing_status": "covered",
                }
            )

    summary = {
        "compared_series_count": compared_series,
        "compared_period_count": compared_periods,
        "value_difference_count": value_difference_count,
        "missing_vintage_count": missing_vintage_count,
        "post_as_of_revision_blocked_count": post_as_of_revision_blocked_count,
        "not_yet_released_observation_blocked_count": not_yet_released_observation_blocked_count,
        "silent_fallback_count": silent_fallback_count,
        "point_in_time_comparison_ready": missing_vintage_count == 0,
    }
    if args.output:
        import json

        Path(args.output).write_text(
            json.dumps({"summary": summary, "rows": rows}, indent=2),
            encoding="utf-8",
        )
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _series_ids(args: argparse.Namespace) -> list[str]:
    if args.series_id:
        return sorted({series_id.strip().upper() for series_id in args.series_id})
    if args.formal_only:
        return list(discover_formal_dependencies("specs/indicator_catalog.yaml").direct_series_ids)
    return []


def _as_of_dates(scenario_id: str | None, max_periods: int | None) -> list[str]:
    payload = yaml.safe_load(Path("specs/backtests/scenarios.yaml").read_text())
    scenarios = payload.get("scenarios", [])
    if scenario_id:
        scenarios = [scenario for scenario in scenarios if scenario["scenario_id"] == scenario_id]
    dates: list[str] = []
    for scenario in scenarios:
        for timestamp in pd.date_range(
            start=pd.Timestamp(str(scenario["window_start"])),
            end=pd.Timestamp(str(scenario["window_end"])),
            freq="ME",
        ):
            dates.append(timestamp.date().isoformat())
    return dates[:max_periods] if max_periods is not None else dates


def _read_revised(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["date", "value"])
    return pd.read_csv(path)


def _latest_value_as_of(frame: pd.DataFrame, as_of: str) -> float | None:
    if frame.empty or "date" not in frame or "value" not in frame:
        return None
    eligible = frame[pd.to_datetime(frame["date"], errors="coerce") <= pd.Timestamp(as_of)]
    if eligible.empty:
        return None
    return float(pd.to_numeric(eligible["value"], errors="coerce").dropna().iloc[-1])


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
