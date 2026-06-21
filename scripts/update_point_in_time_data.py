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

ALFRED_EARLIEST_REALTIME_START = "1776-07-04"


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
    as_of_start = args.as_of_start or (ALFRED_EARLIEST_REALTIME_START if as_of_dates else None)
    as_of_end = args.as_of_end or (_window_end(as_of_dates) if as_of_dates else None)

    exact = initial = proxy = unsupported = reused = written = failed = api_requests = 0
    pagination_requests = 0
    bulk_series_query_count = 0
    api_requests_by_series: dict[str, int] = {}
    blockers: dict[str, str] = {}
    series_summaries: list[dict[str, object]] = []
    provider = None
    api_available = bool(os.getenv("FRED_API_KEY")) and not args.no_api and not args.dry_run
    if api_available:
        provider = AlfredProvider()

    for series_id in requested:
        repair_corrupt_cache = False
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
                cached = cache.read_series(series_id)
            except PointInTimeCacheError as exc:
                if not api_available or provider is None:
                    failed += 1
                    blockers[series_id] = str(exc)
                    series_summaries.append(
                        _series_summary(
                            series_id=series_id,
                            observation_start=observation_start,
                            observation_end=observation_end,
                            as_of_start=as_of_start,
                            as_of_end=as_of_end,
                            cache_status="corrupt",
                            blocker=str(exc),
                        )
                    )
                    continue
                repair_corrupt_cache = True
            else:
                reused += 1
                series_summaries.append(
                    _series_summary_from_manifest(
                        cached.manifest,
                        observation_start=observation_start,
                        observation_end=observation_end,
                        as_of_start=as_of_start,
                        as_of_end=as_of_end,
                        cache_status="reused",
                    )
                )
                continue
        if args.dry_run:
            series_summaries.append(
                _series_summary(
                    series_id=series_id,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    as_of_start=as_of_start,
                    as_of_end=as_of_end,
                    cache_status="dry_run",
                )
            )
            continue
        if args.no_api:
            failed += 1
            blockers[series_id] = "no-api mode: cache missing or reuse disabled"
            series_summaries.append(
                _series_summary(
                    series_id=series_id,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    as_of_start=as_of_start,
                    as_of_end=as_of_end,
                    cache_status="missing",
                    blocker=blockers[series_id],
                )
            )
            continue
        if not api_available or provider is None:
            failed += 1
            blockers[series_id] = "FRED_API_KEY is not set; strict vintage backfill not attempted"
            series_summaries.append(
                _series_summary(
                    series_id=series_id,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    as_of_start=as_of_start,
                    as_of_end=as_of_end,
                    cache_status="missing",
                    blocker=blockers[series_id],
                )
            )
            continue

        try:
            bulk_series_query_count += 1
            observations = provider.fetch_observations(
                series_id,
                observation_start=observation_start,
                observation_end=observation_end,
                realtime_start=as_of_start,
                realtime_end=as_of_end,
                output_type=1,
            )
            series_request_count = provider.last_request_count
            api_requests += series_request_count
            pagination_requests += provider.last_pagination_count
            api_requests_by_series[series_id] = series_request_count
            manifest = cache.write_series(
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
                force=args.force or repair_corrupt_cache,
            )
        except (AlfredProviderError, PointInTimeCacheError) as exc:
            failed += 1
            blockers[series_id] = str(exc)
            series_summaries.append(
                _series_summary(
                    series_id=series_id,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    as_of_start=as_of_start,
                    as_of_end=as_of_end,
                    response_row_count=0,
                    pagination_count=provider.last_pagination_count if provider else 0,
                    cache_status="failed",
                    blocker=str(exc),
                )
            )
            continue
        written += 1
        series_summaries.append(
            _series_summary_from_manifest(
                manifest,
                observation_start=observation_start,
                observation_end=observation_end,
                as_of_start=as_of_start,
                as_of_end=as_of_end,
                response_row_count=len(observations),
                pagination_count=provider.last_pagination_count,
                cache_status="written",
            )
        )

    result = "passed" if failed == 0 and requested else "blocked"
    average_requests = (
        round(api_requests / len(api_requests_by_series), 6) if api_requests_by_series else 0.0
    )
    summary = {
        "fred_api_key_present": bool(os.getenv("FRED_API_KEY")),
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
        "bulk_series_query_count": bulk_series_query_count,
        "pagination_request_count": pagination_requests,
        "per_as_of_network_request_count": 0,
        "monthly_as_of_network_loop_detected": False,
        "average_api_requests_per_series": average_requests,
        "max_api_requests_per_series": max(api_requests_by_series.values(), default=0),
        "cache_dir": str(Path(args.cache_dir)),
        "secret_logged": False,
        "result": result,
    }
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    for series_id, reason in sorted(blockers.items()):
        print(f"blocker series_id={series_id} reason={reason}")
    for item in series_summaries:
        print("series_summary " + " ".join(f"{key}={_format(value)}" for key, value in item.items()))
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


def _series_summary(
    *,
    series_id: str,
    observation_start: str | None,
    observation_end: str | None,
    as_of_start: str | None,
    as_of_end: str | None,
    response_row_count: int = 0,
    pagination_count: int = 0,
    cache_status: str,
    blocker: str = "none",
) -> dict[str, object]:
    return {
        "series_id": series_id,
        "requested_observation_start": observation_start,
        "requested_observation_end": observation_end,
        "requested_realtime_start": as_of_start,
        "requested_realtime_end": as_of_end,
        "query_mode": "vintage_as_of_realtime_periods",
        "response_row_count": response_row_count,
        "pagination_count": pagination_count,
        "cache_row_count": 0,
        "earliest_observation_date": None,
        "latest_observation_date": None,
        "earliest_realtime_start": None,
        "latest_realtime_start": None,
        "scenario_coverage_start": observation_start,
        "scenario_coverage_end": observation_end,
        "exact_vintage_support_verified": False,
        "initial_release_support_verified": False,
        "cache_status": cache_status,
        "blocker_reason": blocker,
    }


def _series_summary_from_manifest(
    manifest: dict[str, Any],
    *,
    observation_start: str | None,
    observation_end: str | None,
    as_of_start: str | None,
    as_of_end: str | None,
    response_row_count: int | None = None,
    pagination_count: int = 0,
    cache_status: str,
) -> dict[str, object]:
    return {
        "series_id": manifest.get("series_id"),
        "requested_observation_start": observation_start,
        "requested_observation_end": observation_end,
        "requested_realtime_start": as_of_start,
        "requested_realtime_end": as_of_end,
        "query_mode": manifest.get("query_mode"),
        "response_row_count": manifest.get("row_count") if response_row_count is None else response_row_count,
        "pagination_count": pagination_count,
        "cache_row_count": manifest.get("row_count"),
        "earliest_observation_date": manifest.get("earliest_observation_date"),
        "latest_observation_date": manifest.get("latest_observation_date"),
        "earliest_realtime_start": manifest.get("earliest_realtime_start"),
        "latest_realtime_start": manifest.get("latest_realtime_start"),
        "scenario_coverage_start": observation_start,
        "scenario_coverage_end": observation_end,
        "exact_vintage_support_verified": bool(manifest.get("row_count")),
        "initial_release_support_verified": False,
        "cache_status": cache_status,
        "blocker_reason": "none",
    }


if __name__ == "__main__":
    raise SystemExit(main())
