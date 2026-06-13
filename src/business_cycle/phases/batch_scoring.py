"""Batch scoring for phase-level results."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.scoring import score_phase
from business_cycle.phases.specs import PhaseScoreResult, PhaseScoringSpec


@dataclass(frozen=True)
class PhaseBatchScoreSummary:
    """Summary of a batch phase scoring run."""

    total_phases: int
    scored_phases: int
    failed_phases: int
    results: list[PhaseScoreResult]
    failures: list[dict[str, str]]


def score_phase_batch_safe(
    phase_specs: dict[str, PhaseScoringSpec],
    indicator_scores: dict[str, IndicatorScoreResult] | list[IndicatorScoreResult],
    as_of: str | date | None = None,
) -> PhaseBatchScoreSummary:
    """Score phases with per-phase failure isolation."""

    results: list[PhaseScoreResult] = []
    failures: list[dict[str, str]] = []

    for phase_id in sorted(phase_specs):
        phase_spec = phase_specs[phase_id]
        try:
            results.append(score_phase(phase_spec, indicator_scores, as_of=as_of))
        except Exception as exc:  # noqa: BLE001 - one bad phase spec should not stop the batch.
            failures.append(
                {
                    "phase_id": phase_id,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )

    return PhaseBatchScoreSummary(
        total_phases=len(phase_specs),
        scored_phases=len(results),
        failed_phases=len(failures),
        results=results,
        failures=failures,
    )


def serialize_phase_score_result(result: PhaseScoreResult) -> dict[str, Any]:
    """Convert a phase score result into a JSON-serializable mapping."""

    return {
        "phase_id": result.phase_id,
        "phase_name_zh": result.phase_name_zh,
        "score": result.score,
        "confidence": result.confidence,
        "available_weight": result.available_weight,
        "missing_indicators": result.missing_indicators,
        "contributing_indicators": _json_safe(result.contributing_indicators),
        "stage_hint": result.stage_hint,
        "reason_zh": result.reason_zh,
        "details": _json_safe(result.details),
    }


def write_phase_scores_json(
    summary: PhaseBatchScoreSummary,
    output_path: str | Path,
) -> Path:
    """Write batch phase scores to JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": {
            "total_phases": summary.total_phases,
            "scored_phases": summary.scored_phases,
            "failed_phases": summary.failed_phases,
        },
        "results": [serialize_phase_score_result(result) for result in summary.results],
        "failures": summary.failures,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_phase_scores_json(path: str | Path) -> dict[str, PhaseScoreResult]:
    """Load Phase 3C phase_scores.json into PhaseScoreResult objects."""

    phase_scores_path = Path(path)
    if not phase_scores_path.exists():
        raise FileNotFoundError(f"Phase scores JSON does not exist: {phase_scores_path}")

    payload = json.loads(phase_scores_path.read_text(encoding="utf-8"))
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("Phase scores JSON must contain results list")

    phase_scores: dict[str, PhaseScoreResult] = {}
    for entry in results:
        if not isinstance(entry, dict):
            raise ValueError("Each phase score result must be a mapping")
        missing = [
            field
            for field in (
                "phase_id",
                "phase_name_zh",
                "score",
                "confidence",
                "available_weight",
                "missing_indicators",
                "contributing_indicators",
                "stage_hint",
                "reason_zh",
                "details",
            )
            if field not in entry
        ]
        if missing:
            raise ValueError(
                f"Phase score result for {entry.get('phase_id', '<unknown>')} "
                f"missing required field(s): {', '.join(missing)}"
            )

        result = PhaseScoreResult(
            phase_id=str(entry["phase_id"]),
            phase_name_zh=str(entry["phase_name_zh"]),
            score=float(entry["score"]),
            confidence=float(entry["confidence"]),
            available_weight=float(entry["available_weight"]),
            missing_indicators=list(entry["missing_indicators"]),
            contributing_indicators=list(entry["contributing_indicators"]),
            stage_hint=None if entry["stage_hint"] is None else str(entry["stage_hint"]),
            reason_zh=str(entry["reason_zh"]),
            details=dict(entry["details"]),
        )
        if result.phase_id in phase_scores:
            raise ValueError(f"Duplicate phase score result: {result.phase_id}")
        phase_scores[result.phase_id] = result

    return phase_scores


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
