"""Manual verifier for FRED candidate series in the indicator catalog."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from business_cycle import data_sources
from business_cycle.indicators.catalog import load_indicator_catalog
from business_cycle.indicators.series_verification import (
    SeriesVerificationResult,
    verify_catalog_series,
)

DEFAULT_CATALOG_PATH = Path("specs/indicator_catalog.yaml")
DEFAULT_OUTPUT_PATH = Path("data/derived/fred_catalog_verification.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify FRED candidate series in the catalog.")
    parser.add_argument(
        "--catalog-path",
        default=str(DEFAULT_CATALOG_PATH),
        help="Indicator catalog YAML path.",
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="JSON output path. Default is ignored data/derived output.",
    )
    parser.add_argument(
        "--series-id",
        action="append",
        help="Only verify a specific FRED series ID. Can be passed multiple times.",
    )
    parser.add_argument(
        "--indicator-id",
        action="append",
        help="Only verify a specific indicator ID. Can be passed multiple times.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    provider = data_sources.FredProvider()
    try:
        provider.require_api_key()
    except data_sources.FredProviderError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    entries = load_indicator_catalog(args.catalog_path)
    entries = filter_catalog_entries(
        entries,
        indicator_ids=args.indicator_id,
        series_ids=args.series_id,
    )
    results = verify_catalog_series(entries, {"fred": provider})
    write_results(Path(args.output_path), results)
    print_summary(results)
    return 0


def filter_catalog_entries(
    entries: list[dict],
    *,
    indicator_ids: list[str] | None = None,
    series_ids: list[str] | None = None,
) -> list[dict]:
    indicator_filter = {indicator_id.strip() for indicator_id in indicator_ids or []}
    series_filter = {series_id.strip().upper() for series_id in series_ids or []}
    filtered: list[dict] = []

    for entry in entries:
        if indicator_filter and entry.get("indicator_id") not in indicator_filter:
            continue
        if series_filter:
            candidates = _candidate_series_ids(entry)
            if not candidates.intersection(series_filter):
                continue
            entry = {**entry, "candidate_series": _filtered_candidates(entry, series_filter)}
        filtered.append(entry)
    return filtered


def write_results(path: Path, results: list[SeriesVerificationResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "results": [result.to_dict() for result in results],
        "summary": summary_counts(results),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def print_summary(results: list[SeriesVerificationResult]) -> None:
    summary = summary_counts(results)
    print(
        "summary "
        f"total={summary['total']} ok={summary['ok']} failed={summary['failed']} "
        f"missing={summary['missing']} unsupported={summary['unsupported']}"
    )
    for result in results:
        if result.status != "ok":
            print(
                "failure "
                f"indicator_id={result.indicator_id} series_id={result.series_id} "
                f"status={result.status} message={result.message}"
            )


def summary_counts(results: list[SeriesVerificationResult]) -> dict[str, int]:
    counts = Counter(result.status for result in results)
    return {
        "total": len(results),
        "ok": counts["ok"],
        "failed": counts["download_failed"] + counts["empty_observations"],
        "missing": counts["missing_candidate_series"],
        "unsupported": counts["provider_not_supported"],
    }


def _candidate_series_ids(entry: dict) -> set[str]:
    return {
        candidate["series_id"]
        for candidate in _normalized_candidates(entry)
        if candidate.get("series_id")
    }


def _filtered_candidates(entry: dict, series_filter: set[str]) -> list[dict[str, str]]:
    return [
        candidate
        for candidate in _normalized_candidates(entry)
        if candidate["series_id"] in series_filter
    ]


def _normalized_candidates(entry: dict) -> list[dict[str, str]]:
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
            candidates.append(
                {
                    "provider": str(entry.get("provider", "fred")).lower(),
                    "series_id": raw_item.strip().upper(),
                }
            )
        elif isinstance(raw_item, dict) and isinstance(raw_item.get("series_id"), str):
            candidates.append(
                {
                    "provider": str(raw_item.get("provider", entry.get("provider", "fred"))).lower(),
                    "series_id": raw_item["series_id"].strip().upper(),
                }
            )
    return candidates


if __name__ == "__main__":
    raise SystemExit(main())

