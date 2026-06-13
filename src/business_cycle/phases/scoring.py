"""Phase score aggregation from indicator-level scores."""

from __future__ import annotations

from datetime import date

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.specs import PhaseScoreResult, PhaseScoringSpec


def score_phase(
    phase_spec: PhaseScoringSpec,
    indicator_scores: dict[str, IndicatorScoreResult] | list[IndicatorScoreResult],
    as_of: str | date | None = None,
) -> PhaseScoreResult:
    """Aggregate indicator scores into one phase score.

    This function scores only the provided phase. It does not select a current phase.
    """

    scores_by_indicator = _scores_by_indicator(indicator_scores)
    contributing_indicators: list[dict] = []
    missing_indicators: list[str] = []
    raw_weighted_score = 0.0
    available_weight = 0.0
    weighted_confidence = 0.0

    for indicator_weight in phase_spec.indicators:
        indicator_score = scores_by_indicator.get(indicator_weight.indicator_id)
        if indicator_score is None:
            missing_indicators.append(indicator_weight.indicator_id)
            continue

        phase_signal_score = _phase_signal_score(indicator_score.score, indicator_weight.signal_transform)
        weighted_contribution = phase_signal_score * indicator_weight.weight
        raw_weighted_score += weighted_contribution
        available_weight += indicator_weight.weight
        weighted_confidence += indicator_score.confidence * indicator_weight.weight
        contributing_indicators.append(
            {
                "indicator_id": indicator_weight.indicator_id,
                "original_score": indicator_score.score,
                "phase_signal_score": phase_signal_score,
                "confidence": indicator_score.confidence,
                "weight": indicator_weight.weight,
                "weighted_contribution": weighted_contribution,
                "role": indicator_weight.role,
                "signal_transform": indicator_weight.signal_transform,
            }
        )

    score = raw_weighted_score / available_weight if available_weight > 0.0 else 0.0
    base_confidence = weighted_confidence / available_weight if available_weight > 0.0 else 0.0
    confidence = _phase_confidence(
        base_confidence=base_confidence,
        available_weight=available_weight,
        minimum_available_weight=phase_spec.minimum_available_weight,
        missing_indicators=missing_indicators,
        phase_spec=phase_spec,
    )
    stage_hint = _stage_hint(score, phase_spec.early_mid_late_thresholds)
    reason_zh = _reason_zh(
        phase_score=score,
        available_weight=available_weight,
        minimum_available_weight=phase_spec.minimum_available_weight,
        contributing_indicators=contributing_indicators,
        missing_indicators=missing_indicators,
    )

    return PhaseScoreResult(
        phase_id=phase_spec.phase_id,
        phase_name_zh=phase_spec.phase_name_zh,
        score=_clamp_score(score),
        confidence=_clamp_confidence(confidence),
        available_weight=_clamp_confidence(available_weight),
        missing_indicators=missing_indicators,
        contributing_indicators=contributing_indicators,
        stage_hint=stage_hint,
        reason_zh=reason_zh,
        details={
            "raw_weighted_score": raw_weighted_score,
            "available_weight": available_weight,
            "minimum_available_weight": phase_spec.minimum_available_weight,
            "missing_indicators": missing_indicators,
            "confidence_policy": phase_spec.confidence_policy,
            "stage_thresholds": phase_spec.early_mid_late_thresholds,
            "signal_transforms": {
                indicator.indicator_id: indicator.signal_transform
                for indicator in phase_spec.indicators
            },
            "as_of": None if as_of is None else str(as_of),
        },
    )


def score_phase_batch(
    phase_specs: dict[str, PhaseScoringSpec],
    indicator_scores: dict[str, IndicatorScoreResult] | list[IndicatorScoreResult],
    as_of: str | date | None = None,
) -> dict[str, PhaseScoreResult]:
    """Score every provided phase spec without selecting a current phase."""

    return {
        phase_id: score_phase(phase_spec, indicator_scores, as_of=as_of)
        for phase_id, phase_spec in sorted(phase_specs.items())
    }


def _scores_by_indicator(
    indicator_scores: dict[str, IndicatorScoreResult] | list[IndicatorScoreResult],
) -> dict[str, IndicatorScoreResult]:
    if isinstance(indicator_scores, dict):
        return dict(indicator_scores)
    return {score.indicator_id: score for score in indicator_scores}


def _phase_signal_score(original_score: float, signal_transform: str) -> float:
    if signal_transform == "as_is":
        return original_score
    if signal_transform == "inverted":
        return 100.0 - original_score
    raise ValueError(f"Unsupported signal_transform: {signal_transform}")


def _phase_confidence(
    *,
    base_confidence: float,
    available_weight: float,
    minimum_available_weight: float,
    missing_indicators: list[str],
    phase_spec: PhaseScoringSpec,
) -> float:
    confidence = base_confidence * available_weight
    if available_weight < minimum_available_weight:
        ratio = available_weight / minimum_available_weight if minimum_available_weight > 0 else 0.0
        confidence *= max(0.0, min(1.0, ratio))

    confidence -= _missing_role_penalty(missing_indicators, phase_spec)
    return _clamp_confidence(confidence)


def _missing_role_penalty(missing_indicators: list[str], phase_spec: PhaseScoringSpec) -> float:
    if not missing_indicators:
        return 0.0

    policy = phase_spec.confidence_policy
    penalty_by_role = {
        "core": float(policy.get("missing_core_indicator_penalty", 0.0)),
        "confirmation": float(policy.get("missing_confirmation_indicator_penalty", 0.0)),
        "warning": float(policy.get("missing_warning_indicator_penalty", 0.0)),
        "optional": float(policy.get("missing_optional_indicator_penalty", 0.0)),
        None: float(policy.get("missing_indicator_penalty", 0.0)),
    }
    role_by_indicator = {
        indicator.indicator_id: indicator.role
        for indicator in phase_spec.indicators
    }
    return sum(penalty_by_role.get(role_by_indicator.get(indicator_id), 0.0) for indicator_id in missing_indicators)


def _stage_hint(score: float, thresholds: dict[str, float]) -> str | None:
    early = thresholds.get("early")
    mid = thresholds.get("mid")
    late = thresholds.get("late")
    if early is None or mid is None or late is None:
        return None
    if score >= late:
        return "late"
    if score >= mid:
        return "mid"
    if score >= early:
        return "early"
    return None


def _reason_zh(
    *,
    phase_score: float,
    available_weight: float,
    minimum_available_weight: float,
    contributing_indicators: list[dict],
    missing_indicators: list[str],
) -> str:
    top_contributors = sorted(
        contributing_indicators,
        key=lambda indicator: indicator["weighted_contribution"],
        reverse=True,
    )[:3]
    top_text = "、".join(indicator["indicator_id"] for indicator in top_contributors) or "無"
    missing_text = "、".join(missing_indicators) if missing_indicators else "無"
    coverage_text = (
        "可用指標權重低於門檻，confidence 已下調。"
        if available_weight < minimum_available_weight
        else "可用指標權重達到最低門檻。"
    )
    return (
        f"phase score 為 {phase_score:.1f}，available_weight 為 {available_weight:.2f}。"
        f"主要貢獻指標：{top_text}。缺失指標：{missing_text}。{coverage_text}"
    )


def _clamp_score(value: float) -> float:
    return float(min(100.0, max(0.0, value)))


def _clamp_confidence(value: float) -> float:
    return float(min(1.0, max(0.0, value)))
