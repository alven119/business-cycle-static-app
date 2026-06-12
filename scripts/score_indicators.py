"""Score indicators from local raw CSV cache."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from business_cycle.indicators.batch_scoring import (
    IndicatorBatchScoreSummary,
    score_indicator_batch,
    write_indicator_scores_json,
)
from business_cycle.indicators.catalog import load_indicator_catalog, load_indicator_scoring_specs

DEFAULT_CATALOG_PATH = Path("specs/indicator_catalog.yaml")
DEFAULT_INPUT_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path("data/derived/indicator_scores.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score indicators from local raw CSV cache.")
    parser.add_argument(
        "--catalog-path",
        default=str(DEFAULT_CATALOG_PATH),
        help="Indicator catalog YAML path.",
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help="Directory containing raw provider CSV files.",
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="JSON output path.",
    )
    parser.add_argument("--as-of", help="Optional scoring date in YYYY-MM-DD format.")
    parser.add_argument(
        "--indicator-id",
        action="append",
        help="Only score a specific indicator ID. Can be passed multiple times.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    specs = load_indicator_scoring_specs(args.catalog_path)
    catalog_entries = load_indicator_catalog(args.catalog_path)
    specs = filter_specs(specs, indicator_ids=args.indicator_id)
    catalog_entries = filter_entries(catalog_entries, indicator_ids=args.indicator_id)

    observations_by_indicator, load_failures = load_observations_by_indicator(
        catalog_entries,
        input_dir=Path(args.input_dir),
    )
    summary = score_indicator_batch(observations_by_indicator, specs, as_of=args.as_of)
    summary = IndicatorBatchScoreSummary(
        total_indicators=summary.total_indicators,
        scored_indicators=summary.scored_indicators,
        failed_indicators=summary.failed_indicators + len(load_failures),
        results=summary.results,
        failures=load_failures + summary.failures,
    )

    output_path = write_indicator_scores_json(summary, args.output_path)
    print(
        "summary "
        f"total={summary.total_indicators} scored={summary.scored_indicators} "
        f"failed={summary.failed_indicators} output={output_path}"
    )
    return 0


def filter_specs(
    specs: dict[str, Any],
    *,
    indicator_ids: list[str] | None,
) -> dict[str, Any]:
    if not indicator_ids:
        return specs
    wanted = set(indicator_ids)
    return {indicator_id: spec for indicator_id, spec in specs.items() if indicator_id in wanted}


def filter_entries(
    entries: list[dict[str, Any]],
    *,
    indicator_ids: list[str] | None,
) -> list[dict[str, Any]]:
    if not indicator_ids:
        return entries
    wanted = set(indicator_ids)
    return [entry for entry in entries if entry.get("indicator_id") in wanted]


def load_observations_by_indicator(
    entries: list[dict[str, Any]],
    *,
    input_dir: Path,
) -> tuple[dict[str, pd.DataFrame], list[dict[str, str]]]:
    observations_by_indicator: dict[str, pd.DataFrame] = {}
    failures: list[dict[str, str]] = []

    for entry in entries:
        indicator_id = str(entry.get("indicator_id", ""))
        series_id = first_fred_candidate_series_id(entry)
        if series_id is None:
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingCandidateSeries",
                    "message": "No FRED candidate_series configured for this indicator.",
                }
            )
            continue

        csv_path = input_dir / f"{series_id}.csv"
        if not csv_path.exists():
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingRawCsv",
                    "message": f"Raw CSV not found: {csv_path}",
                }
            )
            continue

        try:
            observations_by_indicator[indicator_id] = pd.read_csv(csv_path)
        except Exception as exc:  # noqa: BLE001 - one bad CSV should not stop the batch.
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )

    return observations_by_indicator, failures


def first_fred_candidate_series_id(entry: dict[str, Any]) -> str | None:
    raw_candidates = entry.get("candidate_series")
    if isinstance(raw_candidates, str):
        return raw_candidates.strip().upper()
    if isinstance(raw_candidates, dict):
        return _candidate_series_id_if_fred(raw_candidates, default_provider=str(entry.get("provider", "")))
    if isinstance(raw_candidates, list):
        for candidate in raw_candidates:
            if isinstance(candidate, str):
                return candidate.strip().upper()
            if isinstance(candidate, dict):
                series_id = _candidate_series_id_if_fred(
                    candidate,
                    default_provider=str(entry.get("provider", "")),
                )
                if series_id is not None:
                    return series_id
    return None


def _candidate_series_id_if_fred(candidate: dict[str, Any], *, default_provider: str) -> str | None:
    provider = str(candidate.get("provider", default_provider)).lower()
    series_id = candidate.get("series_id")
    if provider != "fred" or not isinstance(series_id, str):
        return None
    return series_id.strip().upper()


if __name__ == "__main__":
    raise SystemExit(main())

