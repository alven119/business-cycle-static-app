from __future__ import annotations

from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import (
    PhaseStateMachineConfig,
    resolve_current_phase,
)


def config() -> PhaseStateMachineConfig:
    return PhaseStateMachineConfig(
        phase_order=["recession", "recovery", "growth", "boom"],
        min_phase_confidence=0.65,
        min_available_weight=0.70,
        min_score_for_initial_estimate=65.0,
        min_score_margin=8.0,
        transition_score_margin=5.0,
        allow_initial_estimate=True,
    )


def phase_score(
    phase_id: str,
    score: float,
    confidence: float = 0.85,
    available_weight: float = 1.0,
) -> PhaseScoreResult:
    return PhaseScoreResult(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        score=score,
        confidence=confidence,
        available_weight=available_weight,
        missing_indicators=[],
        contributing_indicators=[],
        stage_hint=None,
        reason_zh="synthetic",
        details={},
    )


def test_initial_estimate_when_top_score_passes_thresholds_and_margin() -> None:
    decision = resolve_current_phase(
        [
            phase_score("recovery", 82),
            phase_score("growth", 70),
            phase_score("boom", 55),
            phase_score("recession", 40),
        ],
        config(),
    )

    assert decision.decision_status == "initial_estimate"
    assert decision.current_phase_id == "recovery"
    assert decision.candidate_phase_id == "recovery"
    assert decision.confidence > 0.0


def test_initial_estimate_rejects_low_confidence_top_score() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 90, confidence=0.50), phase_score("growth", 70)],
        config(),
    )

    assert decision.decision_status == "insufficient_evidence"
    assert decision.current_phase_id is None


def test_initial_estimate_rejects_small_margin_between_top_two() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 80), phase_score("growth", 76)],
        config(),
    )

    assert decision.decision_status == "insufficient_evidence"
    assert decision.current_phase_id is None


def test_previous_recovery_confirms_transition_to_growth() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.decision_status == "confirmed"
    assert decision.current_phase_id == "growth"
    assert decision.allowed_next_phase_id == "growth"
    assert "確認從復甦期轉換到成長期" in decision.reason_zh
    assert "recovery" not in decision.reason_zh
    assert "growth" not in decision.reason_zh


def test_previous_recovery_growth_improves_but_margin_is_watch() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 73)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.decision_status == "transition_watch"
    assert decision.current_phase_id == "recovery"
    assert decision.candidate_phase_id == "growth"
    assert "成長期已有改善跡象" in decision.reason_zh
    assert "暫時維持復甦期" in decision.reason_zh
    assert "recovery" not in decision.reason_zh
    assert "growth" not in decision.reason_zh


def test_non_adjacent_high_score_is_blocked() -> None:
    decision = resolve_current_phase(
        [
            phase_score("recovery", 64),
            phase_score("growth", 60),
            phase_score("recession", 92),
        ],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.current_phase_id == "recovery"
    assert "recession" in decision.blocked_phase_ids
    assert decision.allowed_next_phase_id == "growth"
    assert "衰退期" in decision.reason_zh
    assert "recession" not in decision.reason_zh


def test_boom_allows_recession_as_next_phase() -> None:
    decision = resolve_current_phase(
        [phase_score("boom", 70), phase_score("recession", 80)],
        config(),
        previous_phase_id="boom",
    )

    assert decision.decision_status == "confirmed"
    assert decision.current_phase_id == "recession"
    assert decision.allowed_next_phase_id == "recession"
    assert "確認從榮景期轉換到衰退期" in decision.reason_zh
    assert "boom" not in decision.reason_zh
    assert "recession" not in decision.reason_zh


def test_recession_allows_recovery_as_next_phase() -> None:
    decision = resolve_current_phase(
        [phase_score("recession", 68), phase_score("recovery", 76)],
        config(),
        previous_phase_id="recession",
    )

    assert decision.decision_status == "confirmed"
    assert decision.current_phase_id == "recovery"
    assert decision.allowed_next_phase_id == "recovery"


def test_current_phase_low_available_weight_lowers_decision_confidence() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 72, confidence=0.90, available_weight=0.35), phase_score("growth", 60)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.decision_status == "hold_current"
    assert decision.confidence < 0.90


def test_low_phase_confidence_does_not_confirm_transition() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 60), phase_score("growth", 80, confidence=0.40)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.decision_status != "confirmed"
    assert decision.current_phase_id == "recovery"


def test_blocked_phase_ids_are_reported() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 65), phase_score("growth", 64), phase_score("boom", 90)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.blocked_phase_ids == ["boom"]
    assert "榮景期" in decision.reason_zh
    assert "boom" not in decision.reason_zh


def test_hold_current_reason_uses_zh_phase_labels_for_boom_context() -> None:
    decision = resolve_current_phase(
        [phase_score("boom", 70), phase_score("recession", 68)],
        config(),
        previous_phase_id="boom",
    )

    assert decision.decision_status == "hold_current"
    assert "維持榮景期" in decision.reason_zh
    assert "衰退期尚未提供" in decision.reason_zh
    assert "boom" not in decision.reason_zh
    assert "recession" not in decision.reason_zh


def test_unknown_phase_label_fallback_does_not_crash() -> None:
    custom_config = PhaseStateMachineConfig(
        phase_order=["expansion", "boom"],
        min_phase_confidence=0.65,
        min_available_weight=0.70,
        min_score_for_initial_estimate=65.0,
        min_score_margin=8.0,
        transition_score_margin=5.0,
        allow_initial_estimate=True,
    )

    decision = resolve_current_phase(
        [phase_score("expansion", 70), phase_score("boom", 68)],
        custom_config,
        previous_phase_id="expansion",
    )

    assert decision.decision_status == "hold_current"
    assert "維持expansion" in decision.reason_zh
    assert "榮景期尚未提供" in decision.reason_zh


def test_reason_and_details_are_populated() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
    )

    assert decision.reason_zh
    assert "ranked_phase_scores" in decision.details
    assert decision.details["allowed_next_phase_id"] == "growth"
