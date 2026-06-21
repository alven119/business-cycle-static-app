#!/usr/bin/env python
"""Update or inspect the point-in-time vintage cache."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.point_in_time_coverage import (
    discover_formal_dependencies,
    scenario_month_end_dates,
)
from business_cycle.audits.repository_inventory import collect_repository_inventory
from business_cycle.data_sources.alfred_provider import AlfredProvider, AlfredProviderError
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--formal-only", action="store_true")
    group.add_argument("--all-audited", action="store_true")
    parser.add_argument("--series-id", action="append")
    parser.add_argument("--scenario-horizons", action="store_true")
    parser.add_argument("--observation-start")
    parser.add_argument("--observation-end")
    parser.add_argument("--as-of-start")
    parser.add_argument("--as-of-end")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-api", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cache = PointInTimeCache(args.cache_dir)
    registry = _registry_rows()
    requested = _requested_series(args)
    formal_deps = discover_formal_dependencies("specs/indicator_catalog.yaml")
    as_of_dates = scenario_month_end_dates("specs/backtests/scenarios.yaml") if args.scenario_horizons else []
    observation_start = args.observation_start or (_window_start(as_of_dates) if as_of_dates else None)
    observation_end = args.observation_end or (_window_end(as_of_dates) if as_of_dates else None)
    as_of_start = args.as_of_start or (_window_start(as_of_dates) if as_of_dates else None)
    as_of_end = args.as_of_end or (_window_end(as_of_dates) if as_of_dates else None)

    exact = initial = proxy = unsupported = reused = written = failed = api_requests = 0
    blockers: dict[str, str] = {}
    provider = None
    api_available = bool(os.getenv("FRED_API_KEY")) and not args.no_api and not args.dry_run
    if api_available:
        provider = AlfredProvider()

    for series_id in requested:
        row = registry.get(series_id, {})
        status = row.get("temporal_status")
        if status == "exact_vintage_ready":
            exact += 1
        elif status == "initial_release_only":
            initial += 1
        elif status == "proxy_only":
            proxy += 1
        elif status == "unsupported":
            unsupported += 1
            failed += 1
            blockers[series_id] = str(row.get("caveats") or "unsupported")
            continue

        if args.reuse_existing and cache.exists(series_id):
            try:
                cache.read_series(series_id)
            except PointInTimeCacheError as exc:
                failed += 1
                blockers[series_id] = str(exc)
            else:
                reused += 1
            continue
        if args.dry_run:
            continue
        if args.no_api:
            failed += 1
            blockers[series_id] = "no-api mode: cache missing or reuse disabled"
            continue
        if not api_available or provider is None:
            failed += 1
            blockers[series_id] = "FRED_API_KEY is not set; strict vintage backfill not attempted"
            continue

        try:
            observations = provider.fetch_observations(
                series_id,
                observation_start=observation_start,
                observation_end=observation_end,
                realtime_start=as_of_start,
                realtime_end=as_of_end,
                output_type=1,
            )
            api_requests += 1
            cache.write_series(
                series_id,
                [
                    {
                        "series_id": item.series_id,
                        "observation_date": item.observation_date,
                        "value": item.value,
                        "realtime_start": item.realtime_start,
                        "realtime_end": item.realtime_end,
                    }
                    for item in observations
                ],
                query_mode="vintage_as_of_realtime_periods",
                observation_start=observation_start,
                observation_end=observation_end,
                as_of_start=as_of_start,
                as_of_end=as_of_end,
                force=args.force,
            )
        except (AlfredProviderError, PointInTimeCacheError) as exc:
            failed += 1
            blockers[series_id] = str(exc)
            continue
        written += 1

    result = "passed" if failed == 0 and requested else "blocked"
    summary = {
        "requested_series_count": len(requested),
        "formal_indicator_count": formal_deps.formal_indicator_count,
        "direct_dependency_count": len(formal_deps.direct_series_ids),
        "derived_dependency_count": len(formal_deps.derived_series_ids),
        "scenario_count": _scenario_count(),
        "as_of_date_count": len(as_of_dates),
        "exact_vintage_series_count": exact,
        "initial_release_only_series_count": initial,
        "proxy_only_series_count": proxy,
        "unsupported_series_count": unsupported,
        "cache_reused_series_count": reused,
        "cache_written_series_count": written,
        "failed_series_count": failed,
        "api_request_count": api_requests,
        "cache_dir": str(Path(args.cache_dir)),
        "secret_logged": False,
        "result": result,
    }
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    for series_id, reason in sorted(blockers.items()):
        print(f"blocker series_id={series_id} reason={reason}")
    return 0 if result in {"passed", "blocked"} else 1


def _requested_series(args: argparse.Namespace) -> list[str]:
    if args.series_id:
        return sorted({series_id.strip().upper() for series_id in args.series_id})
    if args.formal_only:
        return list(discover_formal_dependencies("specs/indicator_catalog.yaml").direct_series_ids)
    inventory = collect_repository_inventory()
    if args.all_audited:
        return sorted(
            item["inventory_id"].removeprefix("series:")
            for item in inventory["items"]
            if item["inventory_type"] == "direct_series"
        )
    return list(discover_formal_dependencies("specs/indicator_catalog.yaml").direct_series_ids)


def _registry_rows() -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path("specs/common/series_release_lag_registry.yaml").read_text())
    rows = payload["series_release_lag_registry"]["series"]
    return {str(row["series_id"]): row for row in rows}


def _scenario_count() -> int:
    payload = yaml.safe_load(Path("specs/backtests/scenarios.yaml").read_text())
    return len(payload.get("scenarios", []))


def _window_start(dates: list[str]) -> str | None:
    return min(dates) if dates else None


def _window_end(dates: list[str]) -> str | None:
    return max(dates) if dates else None


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
