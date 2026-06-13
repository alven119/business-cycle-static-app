"""Build dashboard-ready cycle snapshot JSON without recalculating scores."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from business_cycle.indicators.batch_scoring import (
    IndicatorBatchScoreSummary,
    serialize_indicator_score_result,
)
from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.batch_scoring import (
    PhaseBatchScoreSummary,
    serialize_phase_score_result,
)
from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import (
    CurrentPhaseDecision,
    serialize_current_phase_decision,
)

PHASE_ORDER = ("recession", "recovery", "growth", "boom")
LOW_DECISION_CONFIDENCE_THRESHOLD = 0.60


@dataclass(frozen=True)
class CycleSnapshot:
    """Dashboard-ready cycle snapshot payload."""

    generated_at: str
    as_of: str | None
    current_phase_decision: dict[str, Any]
    phase_scores: list[dict[str, Any]]
    indicator_scores: list[dict[str, Any]]
    summary: dict[str, Any]
    warnings: list[str]
    failures: dict[str, list[dict[str, str]]]


def build_cycle_snapshot(
    indicator_scores_summary: IndicatorBatchScoreSummary,
    phase_scores_summary: PhaseBatchScoreSummary,
    current_phase_decision: CurrentPhaseDecision | dict[str, Any],
    as_of: str | None = None,
) -> CycleSnapshot:
    """Combine indicator, phase, and current phase outputs into one snapshot."""

    decision = _decision_dict(current_phase_decision)
    indicator_scores = [
        serialize_indicator_score_result(result)
        for result in sorted(
            indicator_scores_summary.results,
            key=lambda result: result.indicator_id,
        )
    ]
    phase_scores = [
        serialize_phase_score_result(result)
        for result in sorted(
            phase_scores_summary.results,
            key=lambda result: (_phase_sort_index(result.phase_id), result.phase_id),
        )
    ]
    blocked_phase_ids = list(decision.get("blocked_phase_ids") or [])
    summary = {
        "current_phase_id": decision.get("current_phase_id"),
        "decision_status": decision.get("decision_status"),
        "decision_confidence": decision.get("confidence"),
        "total_indicators": indicator_scores_summary.total_indicators,
        "scored_indicators": indicator_scores_summary.scored_indicators,
        "failed_indicators": indicator_scores_summary.failed_indicators,
        "total_phases": phase_scores_summary.total_phases,
        "scored_phases": phase_scores_summary.scored_phases,
        "failed_phases": phase_scores_summary.failed_phases,
        "blocked_phase_count": len(blocked_phase_ids),
    }

    return CycleSnapshot(
        generated_at=datetime.now(timezone.utc).isoformat(),
        as_of=as_of,
        current_phase_decision=decision,
        phase_scores=phase_scores,
        indicator_scores=indicator_scores,
        summary=summary,
        warnings=_snapshot_warnings(
            decision=decision,
            indicator_summary=indicator_scores_summary,
            phase_summary=phase_scores_summary,
        ),
        failures={
            "indicator_failures": indicator_scores_summary.failures,
            "phase_failures": phase_scores_summary.failures,
        },
    )


def write_cycle_snapshot_json(snapshot: CycleSnapshot, output_path: str | Path) -> Path:
    """Write cycle snapshot JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(serialize_cycle_snapshot(snapshot), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def serialize_cycle_snapshot(snapshot: CycleSnapshot) -> dict[str, Any]:
    """Convert a CycleSnapshot dataclass to a JSON-safe mapping."""

    return {
        "generated_at": snapshot.generated_at,
        "as_of": snapshot.as_of,
        "current_phase_decision": snapshot.current_phase_decision,
        "phase_scores": snapshot.phase_scores,
        "indicator_scores": snapshot.indicator_scores,
        "summary": snapshot.summary,
        "warnings": snapshot.warnings,
        "failures": snapshot.failures,
    }


def load_indicator_score_summary_json(path: str | Path) -> IndicatorBatchScoreSummary:
    """Load Phase 2F indicator_scores.json with summary and failures."""

    payload = _load_json_mapping(path, "Indicator scores JSON")
    summary = _summary_mapping(payload, "Indicator scores JSON")
    results = payload.get("results")
    failures = payload.get("failures", [])
    if not isinstance(results, list):
        raise ValueError("Indicator scores JSON must contain results list")
    if not isinstance(failures, list):
        raise ValueError("Indicator scores JSON field 'failures' must be a list")

    return IndicatorBatchScoreSummary(
        total_indicators=int(_required_summary_value(summary, "total_indicators")),
        scored_indicators=int(_required_summary_value(summary, "scored_indicators")),
        failed_indicators=int(_required_summary_value(summary, "failed_indicators")),
        results=[_indicator_score_from_dict(entry) for entry in results],
        failures=[dict(item) for item in failures],
    )


def load_phase_score_summary_json(path: str | Path) -> PhaseBatchScoreSummary:
    """Load Phase 3C phase_scores.json with summary and failures."""

    payload = _load_json_mapping(path, "Phase scores JSON")
    summary = _summary_mapping(payload, "Phase scores JSON")
    results = payload.get("results")
    failures = payload.get("failures", [])
    if not isinstance(results, list):
        raise ValueError("Phase scores JSON must contain results list")
    if not isinstance(failures, list):
        raise ValueError("Phase scores JSON field 'failures' must be a list")

    return PhaseBatchScoreSummary(
        total_phases=int(_required_summary_value(summary, "total_phases")),
        scored_phases=int(_required_summary_value(summary, "scored_phases")),
        failed_phases=int(_required_summary_value(summary, "failed_phases")),
        results=[_phase_score_from_dict(entry) for entry in results],
        failures=[dict(item) for item in failures],
    )


def _snapshot_warnings(
    *,
    decision: dict[str, Any],
    indicator_summary: IndicatorBatchScoreSummary,
    phase_summary: PhaseBatchScoreSummary,
) -> list[str]:
    warnings: list[str] = []
    if decision.get("decision_status") == "insufficient_evidence":
        warnings.append("current_phase_decision has insufficient_evidence.")
    if indicator_summary.failed_indicators > 0:
        warnings.append(f"failed_indicators={indicator_summary.failed_indicators}.")
    if phase_summary.failed_phases > 0:
        warnings.append(f"failed_phases={phase_summary.failed_phases}.")
    blocked_phase_ids = decision.get("blocked_phase_ids") or []
    if blocked_phase_ids:
        warnings.append(f"blocked_phase_ids={', '.join(str(item) for item in blocked_phase_ids)}.")
    confidence = float(decision.get("confidence") or 0.0)
    if confidence < LOW_DECISION_CONFIDENCE_THRESHOLD:
        warnings.append(f"current phase decision confidence is low: {confidence:.2f}.")
    return warnings


def _decision_dict(decision: CurrentPhaseDecision | dict[str, Any]) -> dict[str, Any]:
    if isinstance(decision, CurrentPhaseDecision):
        return serialize_current_phase_decision(decision)
    return dict(decision)


def _phase_sort_index(phase_id: str) -> int:
    try:
        return PHASE_ORDER.index(phase_id)
    except ValueError:
        return len(PHASE_ORDER)


def _load_json_mapping(path: str | Path, label: str) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"{label} does not exist: {json_path}")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a mapping")
    return payload


def _summary_mapping(payload: dict[str, Any], label: str) -> dict[str, Any]:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(f"{label} must contain summary mapping")
    return summary


def _required_summary_value(summary: dict[str, Any], field: str) -> Any:
    if field not in summary:
        raise ValueError(f"Summary missing required field: {field}")
    return summary[field]


def _indicator_score_from_dict(entry: Any) -> IndicatorScoreResult:
    if not isinstance(entry, dict):
        raise ValueError("Each indicator score result must be a mapping")
    required = ("indicator_id", "score", "confidence", "as_of", "method", "reason_zh", "details")
    missing = [field for field in required if field not in entry]
    if missing:
        raise ValueError(f"Indicator score result missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["details"], dict):
        raise ValueError("Indicator score result details must be a mapping")
    return IndicatorScoreResult(
        indicator_id=str(entry["indicator_id"]),
        score=float(entry["score"]),
        confidence=float(entry["confidence"]),
        as_of=str(entry["as_of"]),
        method=str(entry["method"]),
        reason_zh=str(entry["reason_zh"]),
        details=dict(entry["details"]),
    )


def _phase_score_from_dict(entry: Any) -> PhaseScoreResult:
    if not isinstance(entry, dict):
        raise ValueError("Each phase score result must be a mapping")
    required = (
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
    missing = [field for field in required if field not in entry]
    if missing:
        raise ValueError(f"Phase score result missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["details"], dict):
        raise ValueError("Phase score result details must be a mapping")
    return PhaseScoreResult(
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
