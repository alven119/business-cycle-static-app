"""Update raw macroeconomic data from configured providers."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from dotenv import load_dotenv

from business_cycle import data_sources
from business_cycle.storage.raw_store import RawCsvStore


DEFAULT_CATALOG_PATH = Path("specs/indicator_catalog.yaml")
DEFAULT_RAW_DIR = Path("data/raw")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update local macroeconomic data cache.")
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help="Indicator catalog YAML path.",
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Raw cache root directory.",
    )
    parser.add_argument(
        "--series-id",
        action="append",
        help="Specific FRED series ID to update. Can be passed multiple times.",
    )
    parser.add_argument(
        "--observation-start",
        help="Optional FRED observation_start date, formatted YYYY-MM-DD.",
    )
    parser.add_argument(
        "--observation-end",
        help="Optional FRED observation_end date, formatted YYYY-MM-DD.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the update command without downloading data.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Download even when a raw CSV cache already exists.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    series_ids = args.series_id or series_ids_from_catalog(Path(args.catalog))
    if not series_ids:
        print("No FRED series IDs found to update.")
        return 0

    store = RawCsvStore(args.raw_dir)

    if args.dry_run:
        for series_id in series_ids:
            cache_status = "cached" if store.exists("fred", series_id) else "not_cached"
            print(f"dry-run fred series={series_id} cache={cache_status}")
        return 0

    provider = data_sources.FredProvider()
    for series_id in series_ids:
        if store.exists("fred", series_id) and not args.force_refresh:
            print(f"skip fred series={series_id} cache={store.path_for('fred', series_id)}")
            continue

        try:
            observations = provider.fetch_series_observations(
                series_id,
                observation_start=args.observation_start,
                observation_end=args.observation_end,
            )
        except data_sources.FredProviderError as exc:
            parser.exit(status=1, message=f"error: {exc}\n")

        path = store.write_observations("fred", series_id, observations)
        print(f"wrote fred series={series_id} observations={len(observations)} cache={path}")

    return 0


def series_ids_from_catalog(path: Path) -> list[str]:
    """Read unique FRED series IDs from the indicator catalog."""

    with path.open("r", encoding="utf-8") as yaml_file:
        catalog = yaml.safe_load(yaml_file) or {}

    series_ids: list[str] = []
    seen: set[str] = set()
    for indicator in catalog.get("indicators", []):
        if not isinstance(indicator, dict) or indicator.get("provider") != "fred":
            continue
        for series_id in _fred_series_ids_for_indicator(indicator):
            if series_id not in seen:
                seen.add(series_id)
                series_ids.append(series_id)
    return series_ids


def _fred_series_ids_for_indicator(indicator: dict[object, object]) -> list[str]:
    ids: list[str] = []

    for source in indicator.get("source_priority", []):
        if isinstance(source, dict) and isinstance(source.get("fred"), str):
            ids.append(source["fred"].strip().upper())

    if ids:
        return ids

    for candidate in indicator.get("candidate_fred_series", []):
        if isinstance(candidate, dict) and isinstance(candidate.get("series_id"), str):
            ids.append(candidate["series_id"].strip().upper())

    return ids


if __name__ == "__main__":
    raise SystemExit(main())
