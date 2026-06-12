"""Batch scoring for indicator-level results."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from business_cycle.indicators.dispatcher import score_indicator
from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.indicators.specs import IndicatorScoringSpec


@dataclass(frozen=True)
class IndicatorBatchScoreSummary:
    """Summary of a batch indicator scoring run."""

    total_indicators: int
    scored_indicators: int
    failed_indicators: int
    results: list[IndicatorScoreResult]
    failures: list[dict[str, str]]


def score_indicator_batch(
    observations_by_indicator: dict[str, pd.DataFrame],
    specs: dict[str, IndicatorScoringSpec],
    as_of: str | date | None = None,
) -> IndicatorBatchScoreSummary:
    """Score all indicator specs with deterministic ordering."""

    results: list[IndicatorScoreResult] = []
    failures: list[dict[str, str]] = []

    for indicator_id in sorted(specs):
        spec = specs[indicator_id]
        observations = observations_by_indicator.get(indicator_id)
        if observations is None:
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingObservations",
                    "message": f"No observations provided for indicator {indicator_id!r}.",
                }
            )
            continue

        try:
            results.append(score_indicator(observations, spec, as_of=as_of))
        except Exception as exc:  # noqa: BLE001 - batch scoring must isolate per-indicator failures.
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )

    return IndicatorBatchScoreSummary(
        total_indicators=len(specs),
        scored_indicators=len(results),
        failed_indicators=len(failures),
        results=results,
        failures=failures,
    )


def serialize_indicator_score_result(result: IndicatorScoreResult) -> dict[str, Any]:
    """Convert an indicator score result into a JSON-serializable mapping."""

    return {
        "indicator_id": result.indicator_id,
        "score": result.score,
        "confidence": result.confidence,
        "as_of": result.as_of,
        "method": result.method,
        "reason_zh": result.reason_zh,
        "details": _json_safe(result.details),
    }


def write_indicator_scores_json(
    summary: IndicatorBatchScoreSummary,
    output_path: str | Path,
) -> Path:
    """Write batch indicator scores to JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": {
            "total_indicators": summary.total_indicators,
            "scored_indicators": summary.scored_indicators,
            "failed_indicators": summary.failed_indicators,
        },
        "results": [serialize_indicator_score_result(result) for result in summary.results],
        "failures": summary.failures,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value

