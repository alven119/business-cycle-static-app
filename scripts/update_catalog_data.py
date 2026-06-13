"""Update local raw cache for FRED candidate series in the indicator catalog."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from business_cycle import data_sources
from business_cycle.indicators.catalog import load_indicator_catalog
from business_cycle.storage.raw_store import RawCsvStore

DEFAULT_CATALOG_PATH = Path("specs/indicator_catalog.yaml")
DEFAULT_RAW_DIR = Path("data/raw")


@dataclass(frozen=True)
class CatalogSeriesCandidate:
    indicator_id: str
    provider: str
    series_id: str | None
    status: str = "pending"
    message: str = ""


@dataclass(frozen=True)
class CatalogDataUpdateResult:
    indicator_id: str
    series_id: str | None
    status: str
    cache_path: str | None
    message: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update FRED raw cache from indicator catalog.")
    parser.add_argument(
        "--catalog-path",
        default=str(DEFAULT_CATALOG_PATH),
        help="Indicator catalog YAML path.",
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Raw cache root directory.",
    )
    parser.add_argument(
        "--indicator-id",
        action="append",
        help="Only update a specific indicator ID. Can be passed multiple times.",
    )
    parser.add_argument(
        "--series-id",
        action="append",
        help="Only update a specific FRED series ID. Can be passed multiple times.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Download even when a raw CSV cache already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print candidate series without downloading data.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    entries = load_indicator_catalog(args.catalog_path)
    candidates = catalog_fred_candidates(
        entries,
        indicator_ids=args.indicator_id,
        series_ids=args.series_id,
    )
    store = RawCsvStore(args.raw_dir)

    if args.dry_run:
        results = dry_run_results(candidates, store=store)
        print_results(results)
        return 0

    provider = data_sources.FredProvider()
    try:
        provider.require_api_key()
    except data_sources.FredProviderError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    results = update_catalog_series(
        candidates,
        provider=provider,
        store=store,
        force_refresh=args.force_refresh,
    )
    print_results(results)
    return 0


def catalog_fred_candidates(
    entries: list[dict[str, Any]],
    *,
    indicator_ids: list[str] | None = None,
    series_ids: list[str] | None = None,
) -> list[CatalogSeriesCandidate]:
    indicator_filter = {indicator_id.strip() for indicator_id in indicator_ids or []}
    series_filter = {series_id.strip().upper() for series_id in series_ids or []}
    candidates: list[CatalogSeriesCandidate] = []

    for entry in entries:
        indicator_id = str(entry.get("indicator_id", ""))
        if indicator_filter and indicator_id not in indicator_filter:
            continue
        if str(entry.get("provider", "")).lower() != "fred":
            continue

        series_candidates = _candidate_series(entry)
        if not series_candidates:
            if not series_filter:
                candidates.append(
                    CatalogSeriesCandidate(
                        indicator_id=indicator_id,
                        provider="fred",
                        series_id=None,
                        status="skipped",
                        message="missing_candidate_series",
                    )
                )
            continue

        for candidate in series_candidates:
            series_id = candidate["series_id"]
            if series_filter and series_id not in series_filter:
                continue
            candidates.append(
                CatalogSeriesCandidate(
                    indicator_id=indicator_id,
                    provider="fred",
                    series_id=series_id,
                )
            )

    return candidates


def dry_run_results(
    candidates: list[CatalogSeriesCandidate],
    *,
    store: RawCsvStore,
) -> list[CatalogDataUpdateResult]:
    results: list[CatalogDataUpdateResult] = []
    for candidate in candidates:
        if candidate.series_id is None:
            results.append(
                CatalogDataUpdateResult(
                    indicator_id=candidate.indicator_id,
                    series_id=None,
                    status="skipped",
                    cache_path=None,
                    message=candidate.message or "missing_candidate_series",
                )
            )
            continue
        cache_path = store.path_for("fred", candidate.series_id)
        cache_status = "cached" if cache_path.exists() else "not_cached"
        results.append(
            CatalogDataUpdateResult(
                indicator_id=candidate.indicator_id,
                series_id=candidate.series_id,
                status="skipped",
                cache_path=str(cache_path),
                message=f"dry_run_{cache_status}",
            )
        )
    return results


def update_catalog_series(
    candidates: list[CatalogSeriesCandidate],
    *,
    provider: data_sources.FredProvider,
    store: RawCsvStore,
    force_refresh: bool,
) -> list[CatalogDataUpdateResult]:
    results: list[CatalogDataUpdateResult] = []
    for candidate in candidates:
        if candidate.series_id is None:
            results.append(
                CatalogDataUpdateResult(
                    indicator_id=candidate.indicator_id,
                    series_id=None,
                    status="skipped",
                    cache_path=None,
                    message=candidate.message or "missing_candidate_series",
                )
            )
            continue

        cache_path = store.path_for("fred", candidate.series_id)
        if cache_path.exists() and not force_refresh:
            results.append(
                CatalogDataUpdateResult(
                    indicator_id=candidate.indicator_id,
                    series_id=candidate.series_id,
                    status="skipped",
                    cache_path=str(cache_path),
                    message="cache_exists",
                )
            )
            continue

        try:
            observations = provider.fetch_series_observations(candidate.series_id)
            written_path = store.write_observations("fred", candidate.series_id, observations)
        except data_sources.FredProviderError as exc:
            results.append(
                CatalogDataUpdateResult(
                    indicator_id=candidate.indicator_id,
                    series_id=candidate.series_id,
                    status="failed",
                    cache_path=None,
                    message=str(exc),
                )
            )
            continue

        results.append(
            CatalogDataUpdateResult(
                indicator_id=candidate.indicator_id,
                series_id=candidate.series_id,
                status="updated",
                cache_path=str(written_path),
                message=f"observations={len(observations)}",
            )
        )
    return results


def print_results(results: list[CatalogDataUpdateResult]) -> None:
    for result in results:
        if result.status == "updated":
            print(
                "updated "
                f"indicator_id={result.indicator_id} series_id={result.series_id} "
                f"cache={result.cache_path}"
            )
        elif result.status == "failed":
            print(
                "failure "
                f"indicator_id={result.indicator_id} series_id={result.series_id} "
                f"message={result.message}"
            )
        else:
            print(
                "skipped "
                f"indicator_id={result.indicator_id} series_id={result.series_id} "
                f"message={result.message}"
            )
    summary = summary_counts(results)
    print(
        "summary "
        f"total_series={summary['total_series']} updated_series={summary['updated_series']} "
        f"failed_series={summary['failed_series']} skipped_series={summary['skipped_series']}"
    )


def summary_counts(results: list[CatalogDataUpdateResult]) -> dict[str, int]:
    counts = Counter(result.status for result in results)
    return {
        "total_series": len(results),
        "updated_series": counts["updated"],
        "failed_series": counts["failed"],
        "skipped_series": counts["skipped"],
    }


def _candidate_series(entry: dict[str, Any]) -> list[dict[str, str]]:
    raw_candidates = entry.get("candidate_series")
    if isinstance(raw_candidates, str):
        raw_items = [raw_candidates]
    elif isinstance(raw_candidates, dict):
        raw_items = [raw_candidates]
    elif isinstance(raw_candidates, list):
        raw_items = raw_candidates
    else:
        raw_items = []

    candidates: list[dict[str, str]] = []
    for raw_item in raw_items:
        if isinstance(raw_item, str):
            candidates.append({"provider": "fred", "series_id": raw_item.strip().upper()})
        elif isinstance(raw_item, dict):
            provider = str(raw_item.get("provider", entry.get("provider", ""))).lower()
            series_id = raw_item.get("series_id")
            if provider == "fred" and isinstance(series_id, str):
                candidates.append({"provider": "fred", "series_id": series_id.strip().upper()})
    return candidates


if __name__ == "__main__":
    raise SystemExit(main())
