"""Pure data-only phase resolver wrapper.

This module deliberately accepts only phase scores and model-generated state.
External cycle context, display hints, and dashboard labels are not parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import (
    CurrentPhaseDecision,
    PhaseStateMachineConfig,
    resolve_current_phase,
    serialize_current_phase_decision,
)
from business_cycle.phases.state_machine_catalog import load_phase_state_machine_config
from business_cycle.phases.transition_controls import TransitionControlsConfig


@dataclass(frozen=True)
class DataOnlyDecision:
    """Decision payload plus QA2 provenance metadata."""

    decision: CurrentPhaseDecision
    score_only_candidate: str | None
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = serialize_current_phase_decision(self.decision)
        payload["score_only_candidate"] = self.score_only_candidate
        payload["metadata"] = dict(self.metadata)
        return payload


def resolve_phase_data_only(
    phase_scores: dict[str, float | dict[str, Any] | PhaseScoreResult]
    | list[PhaseScoreResult],
    previous_model_phase: str | None = None,
    phase_history: list[dict[str, Any]] | None = None,
    state_machine_config: PhaseStateMachineConfig | None = None,
    transition_controls: TransitionControlsConfig | None = None,
) -> DataOnlyDecision:
    """Resolve a phase using only scores and model-generated state history."""

    normalized = _normalize_phase_scores(phase_scores)
    config = state_machine_config or load_phase_state_machine_config(
        Path("specs/common/phase_state_machine.yaml")
    )
    decision = resolve_current_phase(
        normalized,
        config,
        previous_phase_id=previous_model_phase,
        transition_controls=transition_controls,
        phase_history=phase_history or [],
    )
    metadata = {
        "decision_mode": "data_only",
        "external_context_used": False,
        "display_hint_used": False,
        "previous_phase_source": (
            "model_state_history" if previous_model_phase is not None else "none"
        ),
        "previous_phase_is_model_generated": previous_model_phase is not None,
        "sequence_constraint_applied": previous_model_phase is not None,
        "transition_controls_applied": transition_controls is not None,
        "provenance_complete": True,
    }
    return DataOnlyDecision(
        decision=decision,
        score_only_candidate=_score_only_candidate(normalized),
        metadata=metadata,
    )


def _normalize_phase_scores(
    phase_scores: dict[str, float | dict[str, Any] | PhaseScoreResult]
    | list[PhaseScoreResult],
) -> list[PhaseScoreResult]:
    if isinstance(phase_scores, list):
        return phase_scores
    results = []
    for phase_id, value in phase_scores.items():
        if isinstance(value, PhaseScoreResult):
            results.append(value)
            continue
        if isinstance(value, dict):
            score = float(value["score"])
            confidence = float(value.get("confidence", 0.85))
            available_weight = float(value.get("available_weight", 1.0))
        else:
            score = float(value)
            confidence = 0.85
            available_weight = 1.0
        results.append(
            PhaseScoreResult(
                phase_id=str(phase_id),
                phase_name_zh=str(phase_id),
                score=score,
                confidence=confidence,
                available_weight=available_weight,
                missing_indicators=[],
                contributing_indicators=[],
                stage_hint=None,
                reason_zh="qa2 synthetic data-only score",
                details={},
            )
        )
    return results


def _score_only_candidate(scores: list[PhaseScoreResult]) -> str | None:
    if not scores:
        return None
    return max(scores, key=lambda item: item.score).phase_id
