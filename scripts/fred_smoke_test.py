"""Manual live smoke test for the FRED provider."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from business_cycle import data_sources
from business_cycle.storage.raw_store import RawCsvStore

DEFAULT_SERIES_IDS = ["UNRATE", "ICSA"]
DEFAULT_RAW_DIR = Path("data/raw")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a small live FRED download smoke test.",
    )
    parser.add_argument(
        "--series-id",
        action="append",
        help="FRED series ID to smoke test. Can be passed multiple times.",
    )
    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Raw cache root directory.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Download even when a raw CSV cache already exists.",
    )
    parser.add_argument(
        "--observation-start",
        default=_default_observation_start(),
        help="FRED observation_start date. Defaults to roughly two years ago.",
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

    store = RawCsvStore(args.raw_dir)
    series_ids = [series_id.strip().upper() for series_id in (args.series_id or DEFAULT_SERIES_IDS)]

    for series_id in series_ids:
        if store.exists("fred", series_id) and not args.force_refresh:
            print(f"skip fred series={series_id} cache={store.path_for('fred', series_id)}")
            continue

        try:
            observations = provider.fetch_series_observations(
                series_id,
                observation_start=args.observation_start,
            )
        except data_sources.FredProviderError as exc:
            parser.exit(status=1, message=f"error: {exc}\n")

        if not observations:
            parser.exit(status=1, message=f"error: FRED series {series_id} returned no observations\n")

        path = store.write_observations("fred", series_id, observations)
        print(f"wrote fred series={series_id} observations={len(observations)} cache={path}")

    return 0


def _default_observation_start() -> str:
    return (date.today() - timedelta(days=730)).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())

