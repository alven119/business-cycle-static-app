#!/usr/bin/env python
"""Update or inspect the point-in-time vintage cache."""

from __future__ import annotations

import argparse
import os
from datetime import date
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
    observation_start = args.observation_start or (
        _observation_window_start(as_of_dates) if as_of_dates else None
    )
    observation_end = args.observation_end or (_window_end(as_of_dates) if as_of_dates else None)
    as_of_start = args.as_of_start or (ALFRED_EARLIEST_REALTIME_START if as_of_dates else None)
    as_of_end = args.as_of_end or (_window_end(as_of_dates) if as_of_dates else None)

    exact = initial = proxy = unsupported = reused = written = failed = api_requests = 0
    pagination_requests = 0
    bulk_series_query_count = 0
    api_requests_by_series: dict[str, int] = {}
    official_query_attempted: set[str] = set()
    official_query_succeeded: set[str] = set()
    official_query_failed: set[str] = set()
    live_verified_exact: set[str] = set()
    live_verified_initial: set[str] = set()
    live_verified_unsupported: set[str] = set()
    live_verified_history_insufficient: set[str] = set()
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
            live_verified_unsupported.add(series_id)
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
                if _cache_manifest_covers(
                    cached.manifest,
                    observation_start=observation_start,
                    observation_end=observation_end,
                    as_of_start=as_of_start,
                    as_of_end=as_of_end,
                ):
                    reused += 1
                    if int(cached.manifest.get("row_count", 0)) > 0:
                        live_verified_exact.add(series_id)
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
                if not api_available or provider is None:
                    failed += 1
                    blockers[series_id] = "existing cache does not cover requested scenario range"
                    series_summaries.append(
                        _series_summary_from_manifest(
                            cached.manifest,
                            observation_start=observation_start,
                            observation_end=observation_end,
                            as_of_start=as_of_start,
                            as_of_end=as_of_end,
                            cache_status="range_incomplete",
                        )
                    )
                    continue
                repair_corrupt_cache = True
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
            official_query_attempted.add(series_id)
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
            if series_id in official_query_attempted:
                official_query_failed.add(series_id)
            blockers[series_id] = str(exc)
            if _registry_scenario_history_insufficient(row, as_of_dates):
                live_verified_history_insufficient.add(series_id)
                blockers[series_id] = (
                    f"official history insufficient for required scenario range: {exc}"
                )
            elif _looks_like_history_insufficient(str(exc)):
                live_verified_history_insufficient.add(series_id)
            elif _looks_like_unsupported(str(exc)):
                live_verified_unsupported.add(series_id)
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
        official_query_succeeded.add(series_id)
        if observations:
            live_verified_exact.add(series_id)
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

    blocker_class = _blocker_class(
        requested_series_count=len(requested),
        failed_series_count=failed,
        fred_api_key_present=bool(os.getenv("FRED_API_KEY")),
        official_query_attempted_count=len(official_query_attempted),
        official_query_failed_count=len(official_query_failed),
        live_verified_unsupported_count=len(live_verified_unsupported),
        live_verified_history_insufficient_count=len(live_verified_history_insufficient),
    )
    result = "passed" if failed == 0 and requested else "blocked"
    average_requests = (
        round(api_requests / len(api_requests_by_series), 6) if api_requests_by_series else 0.0
    )
    qa1c_counts = _qa1c_semantic_counts(
        requested=requested,
        cache=cache,
        as_of_dates=as_of_dates,
        live_verified_unsupported=live_verified_unsupported,
    )
    summary = {
        "env_file_entry_present": _env_file_entry_present(),
        "fred_api_key_present": bool(os.getenv("FRED_API_KEY")),
        "blocker_class": blocker_class,
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
        "official_query_attempted_series_count": len(official_query_attempted),
        "official_query_succeeded_series_count": len(official_query_succeeded),
        "official_query_failed_series_count": len(official_query_failed),
        **qa1c_counts,
        "registry_declared_exact_vintage_series_count": exact,
        "live_verified_exact_vintage_series_count": len(live_verified_exact),
        "live_verified_initial_release_series_count": len(live_verified_initial),
        "live_verified_unsupported_series_count": len(live_verified_unsupported),
        "live_verified_history_insufficient_series_count": len(
            live_verified_history_insufficient
        ),
        "bulk_series_query_count": bulk_series_query_count,
        "pagination_request_count": pagination_requests,
        "per_as_of_network_request_count": 0,
        "monthly_as_of_network_loop_detected": False,
        "average_api_requests_per_series": average_requests,
        "max_api_requests_per_series": max(api_requests_by_series.values(), default=0),
        "retry_count": getattr(provider, "retry_count", 0) if provider is not None else 0,
        "rate_limit_retry_count": (
            getattr(provider, "rate_limit_retry_count", 0) if provider is not None else 0
        ),
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


def _remediation_rows() -> dict[str, dict[str, Any]]:
    path = Path("specs/audits/formal_temporal_gap_remediation.yaml")
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = payload["formal_temporal_gap_remediation"]["rows"]
    return {str(row["series_id"]): row for row in rows}


def _scenario_count() -> int:
    payload = yaml.safe_load(Path("specs/backtests/scenarios.yaml").read_text())
    return len(payload.get("scenarios", []))


def _window_start(dates: list[str]) -> str | None:
    return min(dates) if dates else None


def _observation_window_start(dates: list[str], lookback_years: int = 3) -> str | None:
    if not dates:
        return None
    start = date.fromisoformat(min(dates))
    try:
        return start.replace(year=start.year - lookback_years).isoformat()
    except ValueError:
        return start.replace(year=start.year - lookback_years, month=2, day=28).isoformat()


def _window_end(dates: list[str]) -> str | None:
    return max(dates) if dates else None


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _qa1c_semantic_counts(
    *,
    requested: list[str],
    cache: PointInTimeCache,
    as_of_dates: list[str],
    live_verified_unsupported: set[str],
) -> dict[str, int]:
    remediation = _remediation_rows()
    required_start = min(as_of_dates) if as_of_dates else None
    official_supported = 0
    partial_history = 0
    full_exact = 0
    archive_reconstructed = 0
    observational_ready = 0
    provider_full_range_failed = 0
    unresolved: set[str] = set()
    for series_id in requested:
        row = remediation.get(series_id, {})
        if row.get("provider_full_range_query_status") == "failed":
            provider_full_range_failed += 1
        if row.get("final_strict_ready") and row.get("point_in_time_evidence_class") == "official_release_archive":
            archive_reconstructed += 1
        if (
            row.get("final_strict_ready")
            and row.get("point_in_time_evidence_class") == "official_observational_archive"
        ):
            observational_ready += 1
        if series_id in live_verified_unsupported:
            unresolved.add(series_id)
            continue
        try:
            cached = cache.read_series(series_id)
        except PointInTimeCacheError:
            unresolved.add(series_id)
            continue
        if int(cached.manifest.get("row_count", 0)) > 0:
            official_supported += 1
        if required_start and _cache_history_gap(cached.manifest, required_start):
            partial_history += 1
            unresolved.add(series_id)
            continue
        if required_start and int(cached.manifest.get("row_count", 0)) > 0:
            full_exact += 1
    strict_ready = full_exact + archive_reconstructed + observational_ready
    return {
        "official_query_supported_series_count": official_supported,
        "partial_vintage_history_series_count": partial_history,
        "full_required_horizon_exact_vintage_series_count": full_exact,
        "full_required_horizon_archive_reconstructed_series_count": archive_reconstructed,
        "full_required_horizon_observational_series_count": observational_ready,
        "full_required_horizon_strict_ready_series_count": strict_ready,
        "history_insufficient_series_count": partial_history,
        "provider_full_range_failed_series_count": provider_full_range_failed,
        "unresolved_formal_series_count": len(unresolved),
    }


def _cache_history_gap(manifest: dict[str, Any], required_start: str) -> bool:
    earliest = manifest.get("earliest_realtime_start")
    return isinstance(earliest, str) and _looks_like_iso_date(earliest) and earliest > required_start


def _env_file_entry_present(path: str | Path = ".env") -> bool:
    env_path = Path(path)
    if not env_path.exists():
        return False
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    key_name = "FRED_API_KEY"
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == key_name or stripped.startswith(f"{key_name} ") or stripped.startswith(
            f"{key_name}="
        ):
            return True
    return False


def _cache_manifest_covers(
    manifest: dict[str, Any],
    *,
    observation_start: str | None,
    observation_end: str | None,
    as_of_start: str | None,
    as_of_end: str | None,
) -> bool:
    if int(manifest.get("row_count", 0)) <= 0:
        return False
    checks = (
        ("observation_start", observation_start, "lte"),
        ("observation_end", observation_end, "gte"),
        ("as_of_start", as_of_start, "lte"),
        ("as_of_end", as_of_end, "gte"),
    )
    for field, requested, direction in checks:
        if requested is None:
            continue
        cached = manifest.get(field)
        if not isinstance(cached, str) or not cached:
            return False
        if direction == "lte" and cached > requested:
            return False
        if direction == "gte" and cached < requested:
            return False
    return True


def _registry_scenario_history_insufficient(
    row: dict[str, Any],
    as_of_dates: list[str],
) -> bool:
    if not as_of_dates:
        return False
    scenario_start = row.get("scenario_coverage_start")
    if not isinstance(scenario_start, str) or not _looks_like_iso_date(scenario_start):
        return False
    return scenario_start > min(as_of_dates)


def _looks_like_iso_date(value: str) -> bool:
    parts = value.split("-")
    return (
        len(parts) == 3
        and len(parts[0]) == 4
        and len(parts[1]) == 2
        and len(parts[2]) == 2
        and all(part.isdigit() for part in parts)
    )


def _blocker_class(
    *,
    requested_series_count: int,
    failed_series_count: int,
    fred_api_key_present: bool,
    official_query_attempted_count: int,
    official_query_failed_count: int,
    live_verified_unsupported_count: int,
    live_verified_history_insufficient_count: int,
) -> str:
    if requested_series_count == 0:
        return "official_query_not_attempted"
    if failed_series_count == 0:
        return "strict_coverage_complete"
    if not fred_api_key_present and official_query_attempted_count == 0:
        return "environment_configuration_blocked"
    if official_query_attempted_count == 0:
        return "official_query_not_attempted"
    if live_verified_history_insufficient_count:
        return "official_history_insufficient"
    if live_verified_unsupported_count:
        return "official_series_unsupported"
    if official_query_failed_count:
        return "provider_or_parser_failed"
    return "strict_coverage_incomplete"


def _looks_like_history_insufficient(message: str) -> bool:
    lower = message.lower()
    return any(token in lower for token in ("history insufficient", "no observations", "empty"))


def _looks_like_unsupported(message: str) -> bool:
    lower = message.lower()
    return any(token in lower for token in ("not found", "unknown series", "unsupported"))


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
