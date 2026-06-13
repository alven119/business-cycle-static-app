"""Minimal business-cycle phase state machine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from typing import Literal

from business_cycle.phases.specs import PhaseScoreResult

Phase = Literal["recession", "recovery", "growth", "boom"]
RadarLevel = Literal["none", "watch", "elevated", "confirmed"]

CYCLE_ORDER: tuple[Phase, ...] = ("recession", "recovery", "growth", "boom")
NEXT_PHASE: dict[Phase, Phase] = {
    "recession": "recovery",
    "recovery": "growth",
    "growth": "boom",
    "boom": "recession",
}


@dataclass(frozen=True)
class TransitionThresholds:
    """Thresholds required before a phase transition can be confirmed."""

    target_phase_score_min: float = 0.62
    confidence_min: float = 0.65
    available_weight_min: float = 0.70
    persistence_min_observations: int = 3


@dataclass(frozen=True)
class PhaseEvidence:
    """Inputs needed by the minimal state machine."""

    current_phase: Phase
    target_phase: Phase
    phase_scores: dict[str, float]
    confidence: float
    available_weight: float
    persistence_observations: int
    mixed_evidence: bool = False
    stale_indicators: list[str] = field(default_factory=list)
    missing_indicators: list[str] = field(default_factory=list)
    top_positive_reasons: list[str] = field(default_factory=list)
    top_warning_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PhaseDecision:
    """Structured output from the state machine."""

    current_phase: Phase
    current_substage: str
    phase_scores: dict[str, float]
    transition_radar: RadarLevel
    confidence: float
    available_weight: float
    stale_indicators: list[str]
    top_positive_reasons: list[str]
    top_warning_reasons: list[str]
    missing_data_impact: str
    transitioned: bool
    blocked_reasons: list[str]
    transition_watch: Phase | None


@dataclass(frozen=True)
class CurrentPhaseDecision:
    """Resolver output for the current phase decision."""

    current_phase_id: str | None
    current_phase_name_zh: str | None
    decision_status: str
    previous_phase_id: str | None
    candidate_phase_id: str | None
    candidate_score: float | None
    candidate_confidence: float | None
    current_score: float | None
    confidence: float
    allowed_next_phase_id: str | None
    blocked_phase_ids: list[str]
    reason_zh: str
    details: dict[str, Any]


@dataclass(frozen=True)
class PhaseStateMachineConfig:
    """Config for resolving current phase from phase scores."""

    phase_order: list[str]
    min_phase_confidence: float
    min_available_weight: float
    min_score_for_initial_estimate: float
    min_score_margin: float
    transition_score_margin: float
    allow_initial_estimate: bool


def next_phase_for(phase: Phase) -> Phase:
    """Return the only allowed forward transition target for a phase."""

    _validate_phase(phase)
    return NEXT_PHASE[phase]


def resolve_current_phase(
    phase_scores: dict[str, PhaseScoreResult] | list[PhaseScoreResult],
    config: PhaseStateMachineConfig,
    previous_phase_id: str | None = None,
) -> CurrentPhaseDecision:
    """Resolve the current phase without blindly selecting the highest score."""

    scores_by_phase = _phase_scores_by_id(phase_scores)
    ranked_scores = _ranked_phase_scores(scores_by_phase)
    config_dict = _config_details(config)

    if not scores_by_phase:
        return _decision(
            current_phase_id=None,
            current_phase_name_zh=None,
            decision_status="insufficient_evidence",
            previous_phase_id=previous_phase_id,
            candidate_phase_id=None,
            candidate_score=None,
            candidate_confidence=None,
            current_score=None,
            confidence=0.0,
            allowed_next_phase_id=None,
            blocked_phase_ids=[],
            reason_zh="沒有可用 phase scores，無法產生 current phase 判斷。",
            details={
                "ranked_phase_scores": ranked_scores,
                "config": config_dict,
                "allowed_next_phase_id": None,
                "blocked_phase_ids": [],
                "score_margin": None,
                "evidence_summary": "no_phase_scores",
            },
        )

    if previous_phase_id is None:
        return _resolve_initial_estimate(scores_by_phase, ranked_scores, config, config_dict)

    _validate_config_phase(previous_phase_id, config)
    allowed_next_phase_id = _next_phase_for_config(previous_phase_id, config)
    blocked_phase_ids = _blocked_non_adjacent_phases(
        scores_by_phase=scores_by_phase,
        previous_phase_id=previous_phase_id,
        allowed_next_phase_id=allowed_next_phase_id,
        config=config,
    )
    current_phase_score = scores_by_phase.get(previous_phase_id)
    next_phase_score = scores_by_phase.get(allowed_next_phase_id)
    current_score = current_phase_score.score if current_phase_score is not None else None
    next_score = next_phase_score.score if next_phase_score is not None else None
    score_margin = (
        None
        if next_score is None or current_score is None
        else next_score - current_score
    )

    if next_phase_score is None:
        confidence = _decision_confidence(current_phase_score, config)
        return _decision(
            current_phase_id=previous_phase_id,
            current_phase_name_zh=_phase_name(current_phase_score),
            decision_status="hold_current",
            previous_phase_id=previous_phase_id,
            candidate_phase_id=None,
            candidate_score=None,
            candidate_confidence=None,
            current_score=current_score,
            confidence=confidence,
            allowed_next_phase_id=allowed_next_phase_id,
            blocked_phase_ids=blocked_phase_ids,
            reason_zh=(
                f"維持 {previous_phase_id}，因為允許的下一階段 {allowed_next_phase_id} "
                "沒有可用 phase score。"
            ),
            details=_resolver_details(
                ranked_scores=ranked_scores,
                config=config_dict,
                allowed_next_phase_id=allowed_next_phase_id,
                blocked_phase_ids=blocked_phase_ids,
                score_margin=score_margin,
                evidence_summary="allowed_next_missing",
            ),
        )

    candidate_passes = _phase_score_passes(next_phase_score, config)
    margin_passes = (
        current_score is not None
        and score_margin is not None
        and score_margin >= config.transition_score_margin
    )
    if candidate_passes and margin_passes:
        confidence = _transition_confidence(next_phase_score, score_margin, config)
        return _decision(
            current_phase_id=allowed_next_phase_id,
            current_phase_name_zh=next_phase_score.phase_name_zh,
            decision_status="confirmed",
            previous_phase_id=previous_phase_id,
            candidate_phase_id=allowed_next_phase_id,
            candidate_score=next_phase_score.score,
            candidate_confidence=next_phase_score.confidence,
            current_score=current_score,
            confidence=confidence,
            allowed_next_phase_id=allowed_next_phase_id,
            blocked_phase_ids=blocked_phase_ids,
            reason_zh=(
                f"確認從 {previous_phase_id} 轉換到 {allowed_next_phase_id}，因為允許的下一階段"
                f"分數 {next_phase_score.score:.1f}、confidence {next_phase_score.confidence:.2f}、"
                f"available_weight {next_phase_score.available_weight:.2f} 均達標，且相對目前階段"
                f"分數差距 {score_margin:.1f} 達到轉換門檻。"
                f"{_blocked_reason_text(blocked_phase_ids)}"
            ),
            details=_resolver_details(
                ranked_scores=ranked_scores,
                config=config_dict,
                allowed_next_phase_id=allowed_next_phase_id,
                blocked_phase_ids=blocked_phase_ids,
                score_margin=score_margin,
                evidence_summary="confirmed_allowed_next_transition",
            ),
        )

    if _has_transition_watch_evidence(next_phase_score, current_phase_score, config):
        confidence = _hold_or_watch_confidence(current_phase_score, next_phase_score, config)
        return _decision(
            current_phase_id=previous_phase_id,
            current_phase_name_zh=_phase_name(current_phase_score),
            decision_status="transition_watch",
            previous_phase_id=previous_phase_id,
            candidate_phase_id=allowed_next_phase_id,
            candidate_score=next_phase_score.score,
            candidate_confidence=next_phase_score.confidence,
            current_score=current_score,
            confidence=confidence,
            allowed_next_phase_id=allowed_next_phase_id,
            blocked_phase_ids=blocked_phase_ids,
            reason_zh=(
                f"{allowed_next_phase_id} 已有改善跡象，但分數差距、confidence 或 available_weight "
                f"尚未同時達標，因此暫時維持 {previous_phase_id} 並列入 transition watch。"
                f"{_blocked_reason_text(blocked_phase_ids)}"
            ),
            details=_resolver_details(
                ranked_scores=ranked_scores,
                config=config_dict,
                allowed_next_phase_id=allowed_next_phase_id,
                blocked_phase_ids=blocked_phase_ids,
                score_margin=score_margin,
                evidence_summary="allowed_next_transition_watch",
            ),
        )

    confidence = _decision_confidence(current_phase_score, config)
    return _decision(
        current_phase_id=previous_phase_id,
        current_phase_name_zh=_phase_name(current_phase_score),
        decision_status="hold_current",
        previous_phase_id=previous_phase_id,
        candidate_phase_id=allowed_next_phase_id,
        candidate_score=next_phase_score.score,
        candidate_confidence=next_phase_score.confidence,
        current_score=current_score,
        confidence=confidence,
        allowed_next_phase_id=allowed_next_phase_id,
        blocked_phase_ids=blocked_phase_ids,
        reason_zh=(
            f"維持 {previous_phase_id}，因為允許的下一階段 {allowed_next_phase_id} "
            "尚未提供足夠的轉換證據。"
            f"{_blocked_reason_text(blocked_phase_ids)}"
        ),
        details=_resolver_details(
            ranked_scores=ranked_scores,
            config=config_dict,
            allowed_next_phase_id=allowed_next_phase_id,
            blocked_phase_ids=blocked_phase_ids,
            score_margin=score_margin,
            evidence_summary="hold_previous_phase",
        ),
    )


def write_current_phase_decision_json(
    decision: CurrentPhaseDecision,
    output_path: str | Path,
) -> Path:
    """Write a current phase decision to JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(serialize_current_phase_decision(decision), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def serialize_current_phase_decision(decision: CurrentPhaseDecision) -> dict[str, Any]:
    """Convert a current phase decision into a JSON-serializable mapping."""

    return {
        "current_phase_id": decision.current_phase_id,
        "current_phase_name_zh": decision.current_phase_name_zh,
        "decision_status": decision.decision_status,
        "previous_phase_id": decision.previous_phase_id,
        "candidate_phase_id": decision.candidate_phase_id,
        "candidate_score": decision.candidate_score,
        "candidate_confidence": decision.candidate_confidence,
        "current_score": decision.current_score,
        "confidence": decision.confidence,
        "allowed_next_phase_id": decision.allowed_next_phase_id,
        "blocked_phase_ids": decision.blocked_phase_ids,
        "reason_zh": decision.reason_zh,
        "details": decision.details,
    }


def decide_phase_transition(
    evidence: PhaseEvidence,
    thresholds: TransitionThresholds | None = None,
) -> PhaseDecision:
    """Evaluate whether the cycle can move to the next phase.

    This minimal Phase 0D implementation supports staying in place or moving
    one step forward. It deliberately rejects jumps and reverse transitions.
    """

    thresholds = thresholds or TransitionThresholds()
    _validate_phase(evidence.current_phase)
    _validate_phase(evidence.target_phase)

    allowed_next = next_phase_for(evidence.current_phase)
    target_score = evidence.phase_scores.get(evidence.target_phase, 0.0)
    blocked_reasons = _blocking_reasons(evidence, thresholds, allowed_next, target_score)

    if evidence.mixed_evidence:
        blocked_reasons.append("mixed_evidence_keeps_current_phase")

    transitioned = not blocked_reasons
    resulting_phase = evidence.target_phase if transitioned else evidence.current_phase
    transition_radar = _transition_radar(transitioned, evidence, blocked_reasons, target_score, thresholds)

    return PhaseDecision(
        current_phase=resulting_phase,
        current_substage="early" if transitioned else "unchanged",
        phase_scores=evidence.phase_scores,
        transition_radar=transition_radar,
        confidence=evidence.confidence,
        available_weight=evidence.available_weight,
        stale_indicators=evidence.stale_indicators,
        top_positive_reasons=evidence.top_positive_reasons,
        top_warning_reasons=evidence.top_warning_reasons,
        missing_data_impact=_missing_data_impact(evidence),
        transitioned=transitioned,
        blocked_reasons=blocked_reasons,
        transition_watch=evidence.target_phase if not transitioned and target_score > 0 else None,
    )


def _blocking_reasons(
    evidence: PhaseEvidence,
    thresholds: TransitionThresholds,
    allowed_next: Phase,
    target_score: float,
) -> list[str]:
    reasons: list[str] = []

    if evidence.target_phase != allowed_next:
        if _is_reverse_transition(evidence.current_phase, evidence.target_phase):
            reasons.append("reverse_transition_not_allowed")
        else:
            reasons.append("phase_jump_not_allowed")

    if target_score < thresholds.target_phase_score_min:
        reasons.append("target_phase_score_below_threshold")
    if evidence.confidence < thresholds.confidence_min:
        reasons.append("confidence_below_threshold")
    if evidence.available_weight < thresholds.available_weight_min:
        reasons.append("available_weight_below_threshold")
    if evidence.persistence_observations < thresholds.persistence_min_observations:
        reasons.append("persistence_below_threshold")

    return reasons


def _transition_radar(
    transitioned: bool,
    evidence: PhaseEvidence,
    blocked_reasons: list[str],
    target_score: float,
    thresholds: TransitionThresholds,
) -> RadarLevel:
    if transitioned:
        return "confirmed"
    if evidence.mixed_evidence:
        return "elevated"
    if target_score >= thresholds.target_phase_score_min and blocked_reasons:
        return "watch"
    return "none"


def _missing_data_impact(evidence: PhaseEvidence) -> str:
    missing_count = len(evidence.missing_indicators)
    stale_count = len(evidence.stale_indicators)
    if missing_count == 0 and stale_count == 0:
        return "none"
    return (
        f"missing_indicators={missing_count}; stale_indicators={stale_count}; "
        "confidence_or_available_weight_should_be_reduced"
    )


def _is_reverse_transition(current_phase: Phase, target_phase: Phase) -> bool:
    current_index = CYCLE_ORDER.index(current_phase)
    target_index = CYCLE_ORDER.index(target_phase)
    return target_index == (current_index - 1) % len(CYCLE_ORDER)


def _validate_phase(phase: str) -> None:
    if phase not in CYCLE_ORDER:
        allowed = ", ".join(CYCLE_ORDER)
        raise ValueError(f"unknown phase {phase!r}; expected one of: {allowed}")


def _phase_scores_by_id(
    phase_scores: dict[str, PhaseScoreResult] | list[PhaseScoreResult],
) -> dict[str, PhaseScoreResult]:
    if isinstance(phase_scores, dict):
        return dict(phase_scores)
    return {score.phase_id: score for score in phase_scores}


def _resolve_initial_estimate(
    scores_by_phase: dict[str, PhaseScoreResult],
    ranked_scores: list[dict[str, Any]],
    config: PhaseStateMachineConfig,
    config_dict: dict[str, Any],
) -> CurrentPhaseDecision:
    if not config.allow_initial_estimate:
        return _decision(
            current_phase_id=None,
            current_phase_name_zh=None,
            decision_status="insufficient_evidence",
            previous_phase_id=None,
            candidate_phase_id=None,
            candidate_score=None,
            candidate_confidence=None,
            current_score=None,
            confidence=0.0,
            allowed_next_phase_id=None,
            blocked_phase_ids=[],
            reason_zh="設定不允許 initial_estimate，因此無 previous_phase_id 時不產生 current phase。",
            details=_resolver_details(
                ranked_scores=ranked_scores,
                config=config_dict,
                allowed_next_phase_id=None,
                blocked_phase_ids=[],
                score_margin=None,
                evidence_summary="initial_estimate_disabled",
            ),
        )

    top = ranked_scores[0]
    candidate = scores_by_phase[top["phase_id"]]
    second_score = ranked_scores[1]["score"] if len(ranked_scores) > 1 else 0.0
    score_margin = candidate.score - second_score
    passes = (
        _phase_score_passes(candidate, config)
        and candidate.score >= config.min_score_for_initial_estimate
        and score_margin >= config.min_score_margin
    )
    if passes:
        confidence = _initial_estimate_confidence(candidate, score_margin, config)
        return _decision(
            current_phase_id=candidate.phase_id,
            current_phase_name_zh=candidate.phase_name_zh,
            decision_status="initial_estimate",
            previous_phase_id=None,
            candidate_phase_id=candidate.phase_id,
            candidate_score=candidate.score,
            candidate_confidence=candidate.confidence,
            current_score=None,
            confidence=confidence,
            allowed_next_phase_id=None,
            blocked_phase_ids=[],
            reason_zh=(
                f"沒有 previous_phase_id，因此只做 initial estimate。{candidate.phase_id} "
                f"分數 {candidate.score:.1f}、confidence {candidate.confidence:.2f}、"
                f"available_weight {candidate.available_weight:.2f} 達標，且與第二名差距 "
                f"{score_margin:.1f} 達到門檻。"
            ),
            details=_resolver_details(
                ranked_scores=ranked_scores,
                config=config_dict,
                allowed_next_phase_id=None,
                blocked_phase_ids=[],
                score_margin=score_margin,
                evidence_summary="initial_estimate_passed",
            ),
        )

    reason = (
        "沒有 previous_phase_id，且最高 phase score 未同時滿足分數、confidence、"
        "available_weight 與第二名差距門檻，因此 evidence insufficient。"
    )
    confidence = _initial_estimate_confidence(candidate, score_margin, config)
    return _decision(
        current_phase_id=None,
        current_phase_name_zh=None,
        decision_status="insufficient_evidence",
        previous_phase_id=None,
        candidate_phase_id=candidate.phase_id,
        candidate_score=candidate.score,
        candidate_confidence=candidate.confidence,
        current_score=None,
        confidence=confidence,
        allowed_next_phase_id=None,
        blocked_phase_ids=[],
        reason_zh=reason,
        details=_resolver_details(
            ranked_scores=ranked_scores,
            config=config_dict,
            allowed_next_phase_id=None,
            blocked_phase_ids=[],
            score_margin=score_margin,
            evidence_summary="initial_estimate_insufficient",
        ),
    )


def _phase_score_passes(score: PhaseScoreResult, config: PhaseStateMachineConfig) -> bool:
    return (
        score.confidence >= config.min_phase_confidence
        and score.available_weight >= config.min_available_weight
    )


def _has_transition_watch_evidence(
    next_phase_score: PhaseScoreResult,
    current_phase_score: PhaseScoreResult | None,
    config: PhaseStateMachineConfig,
) -> bool:
    if next_phase_score.score < config.min_score_for_initial_estimate:
        return False
    if current_phase_score is None:
        return True
    return next_phase_score.score >= current_phase_score.score


def _blocked_non_adjacent_phases(
    *,
    scores_by_phase: dict[str, PhaseScoreResult],
    previous_phase_id: str,
    allowed_next_phase_id: str,
    config: PhaseStateMachineConfig,
) -> list[str]:
    blocked = [
        phase_id
        for phase_id, score in scores_by_phase.items()
        if phase_id not in {previous_phase_id, allowed_next_phase_id}
        and score.score >= config.min_score_for_initial_estimate
    ]
    return sorted(blocked)


def _next_phase_for_config(phase_id: str, config: PhaseStateMachineConfig) -> str:
    _validate_config_phase(phase_id, config)
    index = config.phase_order.index(phase_id)
    return config.phase_order[(index + 1) % len(config.phase_order)]


def _validate_config_phase(phase_id: str, config: PhaseStateMachineConfig) -> None:
    if phase_id not in config.phase_order:
        allowed = ", ".join(config.phase_order)
        raise ValueError(f"unknown phase {phase_id!r}; expected one of: {allowed}")


def _ranked_phase_scores(scores_by_phase: dict[str, PhaseScoreResult]) -> list[dict[str, Any]]:
    return [
        {
            "phase_id": score.phase_id,
            "phase_name_zh": score.phase_name_zh,
            "score": score.score,
            "confidence": score.confidence,
            "available_weight": score.available_weight,
            "stage_hint": score.stage_hint,
        }
        for score in sorted(
            scores_by_phase.values(),
            key=lambda item: (-item.score, item.phase_id),
        )
    ]


def _decision(
    *,
    current_phase_id: str | None,
    current_phase_name_zh: str | None,
    decision_status: str,
    previous_phase_id: str | None,
    candidate_phase_id: str | None,
    candidate_score: float | None,
    candidate_confidence: float | None,
    current_score: float | None,
    confidence: float,
    allowed_next_phase_id: str | None,
    blocked_phase_ids: list[str],
    reason_zh: str,
    details: dict[str, Any],
) -> CurrentPhaseDecision:
    return CurrentPhaseDecision(
        current_phase_id=current_phase_id,
        current_phase_name_zh=current_phase_name_zh,
        decision_status=decision_status,
        previous_phase_id=previous_phase_id,
        candidate_phase_id=candidate_phase_id,
        candidate_score=candidate_score,
        candidate_confidence=candidate_confidence,
        current_score=current_score,
        confidence=_clamp_confidence(confidence),
        allowed_next_phase_id=allowed_next_phase_id,
        blocked_phase_ids=blocked_phase_ids,
        reason_zh=reason_zh,
        details=details,
    )


def _resolver_details(
    *,
    ranked_scores: list[dict[str, Any]],
    config: dict[str, Any],
    allowed_next_phase_id: str | None,
    blocked_phase_ids: list[str],
    score_margin: float | None,
    evidence_summary: str,
) -> dict[str, Any]:
    return {
        "ranked_phase_scores": ranked_scores,
        "config": config,
        "allowed_next_phase_id": allowed_next_phase_id,
        "blocked_phase_ids": blocked_phase_ids,
        "score_margin": score_margin,
        "evidence_summary": evidence_summary,
    }


def _config_details(config: PhaseStateMachineConfig) -> dict[str, Any]:
    return {
        "phase_order": config.phase_order,
        "min_phase_confidence": config.min_phase_confidence,
        "min_available_weight": config.min_available_weight,
        "min_score_for_initial_estimate": config.min_score_for_initial_estimate,
        "min_score_margin": config.min_score_margin,
        "transition_score_margin": config.transition_score_margin,
        "allow_initial_estimate": config.allow_initial_estimate,
    }


def _decision_confidence(
    score: PhaseScoreResult | None,
    config: PhaseStateMachineConfig,
) -> float:
    if score is None:
        return 0.0
    coverage_ratio = score.available_weight / config.min_available_weight
    return score.confidence * min(1.0, max(0.0, coverage_ratio))


def _hold_or_watch_confidence(
    current_score: PhaseScoreResult | None,
    next_score: PhaseScoreResult,
    config: PhaseStateMachineConfig,
) -> float:
    current_confidence = _decision_confidence(current_score, config)
    next_confidence = _decision_confidence(next_score, config)
    return min(current_confidence, next_confidence) if current_score is not None else next_confidence


def _transition_confidence(
    score: PhaseScoreResult,
    score_margin: float,
    config: PhaseStateMachineConfig,
) -> float:
    margin_ratio = score_margin / config.transition_score_margin
    return score.confidence * score.available_weight * min(1.0, max(0.0, margin_ratio))


def _initial_estimate_confidence(
    score: PhaseScoreResult,
    score_margin: float,
    config: PhaseStateMachineConfig,
) -> float:
    margin_ratio = score_margin / config.min_score_margin if config.min_score_margin > 0 else 1.0
    return score.confidence * score.available_weight * min(1.0, max(0.0, margin_ratio))


def _phase_name(score: PhaseScoreResult | None) -> str | None:
    if score is None:
        return None
    return score.phase_name_zh


def _blocked_reason_text(blocked_phase_ids: list[str]) -> str:
    if not blocked_phase_ids:
        return ""
    return f" 非相鄰高分 phase 已被阻擋，不允許跳階段：{', '.join(blocked_phase_ids)}。"


def _clamp_confidence(value: float) -> float:
    return float(min(1.0, max(0.0, value)))
