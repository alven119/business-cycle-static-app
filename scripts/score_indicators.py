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
from business_cycle.indicators.scoring import IndicatorScoreResult

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

    observations_by_indicator, load_failures, selected_inputs = load_observations_by_indicator(
        catalog_entries,
        input_dir=Path(args.input_dir),
    )
    load_failed_indicators = {failure["indicator_id"] for failure in load_failures}
    scorable_specs = {
        indicator_id: spec
        for indicator_id, spec in specs.items()
        if indicator_id not in load_failed_indicators
    }
    summary = score_indicator_batch(observations_by_indicator, scorable_specs, as_of=args.as_of)
    results = add_selected_series_details(summary.results, selected_inputs)
    scoring_failures = add_selected_series_to_failures(summary.failures, selected_inputs)
    summary = IndicatorBatchScoreSummary(
        total_indicators=len(specs),
        scored_indicators=len(results),
        failed_indicators=len(scoring_failures) + len(load_failures),
        results=results,
        failures=load_failures + scoring_failures,
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
) -> tuple[dict[str, pd.DataFrame], list[dict[str, str]], dict[str, dict[str, Any]]]:
    observations_by_indicator: dict[str, pd.DataFrame] = {}
    failures: list[dict[str, str]] = []
    selected_inputs: dict[str, dict[str, Any]] = {}

    for entry in entries:
        indicator_id = str(entry.get("indicator_id", ""))
        candidate_series = fred_candidate_series_ids(entry)
        if not candidate_series:
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingCandidateSeries",
                    "message": (
                        f"indicator_id={indicator_id} candidate_series=[] root_cause="
                        "No FRED candidate_series configured for this indicator."
                    ),
                }
            )
            continue

        expected_paths = [input_dir / f"{series_id}.csv" for series_id in candidate_series]
        read_errors: list[str] = []
        selected_frame: pd.DataFrame | None = None
        selected_series_id: str | None = None
        selected_path: Path | None = None
        for series_id, csv_path in zip(candidate_series, expected_paths):
            if not csv_path.exists():
                continue
            try:
                selected_frame = pd.read_csv(csv_path)
            except Exception as exc:  # noqa: BLE001 - try later candidates before failing.
                read_errors.append(f"series_id={series_id} expected_csv_path={csv_path} root_cause={exc}")
                continue
            selected_series_id = series_id
            selected_path = csv_path
            break

        if selected_frame is None or selected_series_id is None or selected_path is None:
            root_cause = "No candidate raw CSV exists or can be read."
            if read_errors:
                root_cause = f"{root_cause} read_errors=[{'; '.join(read_errors)}]"
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingRawCsv",
                    "message": (
                        f"indicator_id={indicator_id} candidate_series={candidate_series} "
                        f"expected_csv_paths={[str(path) for path in expected_paths]} "
                        f"root_cause={root_cause}"
                    ),
                }
            )
            continue

        observations_by_indicator[indicator_id] = selected_frame
        selected_inputs[indicator_id] = {
            "selected_series_id": selected_series_id,
            "selected_csv_path": str(selected_path),
            "candidate_series": candidate_series,
        }

    return observations_by_indicator, failures, selected_inputs


def add_selected_series_details(
    results: list[IndicatorScoreResult],
    selected_inputs: dict[str, dict[str, Any]],
) -> list[IndicatorScoreResult]:
    enriched: list[IndicatorScoreResult] = []
    for result in results:
        selected_input = selected_inputs.get(result.indicator_id, {})
        details = {
            **result.details,
            "selected_series_id": selected_input.get("selected_series_id"),
            "selected_csv_path": selected_input.get("selected_csv_path"),
            "candidate_series": selected_input.get("candidate_series", []),
        }
        enriched.append(
            IndicatorScoreResult(
                indicator_id=result.indicator_id,
                score=result.score,
                confidence=result.confidence,
                as_of=result.as_of,
                method=result.method,
                reason_zh=result.reason_zh,
                details=details,
            )
        )
    return enriched


def add_selected_series_to_failures(
    failures: list[dict[str, str]],
    selected_inputs: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for failure in failures:
        indicator_id = failure.get("indicator_id", "")
        selected_input = selected_inputs.get(indicator_id, {})
        selected_series_id = selected_input.get("selected_series_id")
        selected_csv_path = selected_input.get("selected_csv_path")
        candidate_series = selected_input.get("candidate_series", [])
        message = (
            f"indicator_id={indicator_id} selected_series_id={selected_series_id} "
            f"candidate_series={candidate_series} expected_csv_path={selected_csv_path} "
            f"root_cause={failure.get('message', '')}"
        )
        enriched.append({**failure, "message": message})
    return enriched


def first_fred_candidate_series_id(entry: dict[str, Any]) -> str | None:
    series_ids = fred_candidate_series_ids(entry)
    return series_ids[0] if series_ids else None


def fred_candidate_series_ids(entry: dict[str, Any]) -> list[str]:
    series_ids: list[str] = []
    seen: set[str] = set()
    for series_id in _raw_fred_candidate_series_ids(entry):
        if series_id not in seen:
            seen.add(series_id)
            series_ids.append(series_id)
    return series_ids


def _raw_fred_candidate_series_ids(entry: dict[str, Any]) -> list[str]:
    raw_candidates = entry.get("candidate_series")
    if isinstance(raw_candidates, str):
        return [raw_candidates.strip().upper()]
    if isinstance(raw_candidates, dict):
        series_id = _candidate_series_id_if_fred(raw_candidates, default_provider=str(entry.get("provider", "")))
        return [] if series_id is None else [series_id]
    if isinstance(raw_candidates, list):
        series_ids: list[str] = []
        for candidate in raw_candidates:
            if isinstance(candidate, str):
                series_ids.append(candidate.strip().upper())
            if isinstance(candidate, dict):
                series_id = _candidate_series_id_if_fred(
                    candidate,
                    default_provider=str(entry.get("provider", "")),
                )
                if series_id is not None:
                    series_ids.append(series_id)
        return series_ids
    return []


def _candidate_series_id_if_fred(candidate: dict[str, Any], *, default_provider: str) -> str | None:
    provider = str(candidate.get("provider", default_provider)).lower()
    series_id = candidate.get("series_id")
    if provider != "fred" or not isinstance(series_id, str):
        return None
    return series_id.strip().upper()


if __name__ == "__main__":
    raise SystemExit(main())
