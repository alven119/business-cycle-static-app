"""Minimal business-cycle phase state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

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


def next_phase_for(phase: Phase) -> Phase:
    """Return the only allowed forward transition target for a phase."""

    _validate_phase(phase)
    return NEXT_PHASE[phase]


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

