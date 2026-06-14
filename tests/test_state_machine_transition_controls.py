from __future__ import annotations

from dataclasses import replace

from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import (
    PhaseStateMachineConfig,
    resolve_current_phase,
    serialize_current_phase_decision,
)
from business_cycle.phases.transition_controls import (
    BreadthConfirmationControl,
    ConfirmationPeriodControl,
    CooldownPeriodControl,
    HysteresisMarginControl,
    TransitionControlsConfig,
    TransitionWatchRequiredControl,
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


def phase_score(phase_id: str, score: float) -> PhaseScoreResult:
    return PhaseScoreResult(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        score=score,
        confidence=0.85,
        available_weight=1.0,
        missing_indicators=[],
        contributing_indicators=[],
        stage_hint=None,
        reason_zh="synthetic",
        details={},
    )


def controls(
    *,
    enabled: bool = True,
    transition_watch_required: bool = False,
    confirmation_period: int | None = None,
    hysteresis_margin: float | None = None,
    cooldown_period: int | None = None,
    breadth_confirmation: bool = False,
) -> TransitionControlsConfig:
    return TransitionControlsConfig(
        version=1,
        enabled=enabled,
        description_zh="test",
        transition_watch_required=TransitionWatchRequiredControl(enabled=transition_watch_required),
        confirmation_period=ConfirmationPeriodControl(
            enabled=confirmation_period is not None,
            required_periods=confirmation_period or 1,
        ),
        hysteresis_margin=HysteresisMarginControl(
            enabled=hysteresis_margin is not None,
            min_score_margin=hysteresis_margin or 0.0,
        ),
        cooldown_period=CooldownPeriodControl(
            enabled=cooldown_period is not None,
            periods_after_confirmed=cooldown_period or 0,
        ),
        breadth_confirmation=BreadthConfirmationControl(enabled=breadth_confirmation, min_group_count=2),
        caveats_zh=["使用修訂後歷史資料。", "不構成投資建議。"],
    )


def confirmed_baseline():
    return resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
    )


def test_controls_none_keeps_baseline_result() -> None:
    baseline = confirmed_baseline()
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=None,
    )

    assert serialize_current_phase_decision(decision) == serialize_current_phase_decision(baseline)


def test_disabled_controls_keep_baseline_result() -> None:
    baseline = confirmed_baseline()
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(enabled=False, transition_watch_required=True),
    )

    assert serialize_current_phase_decision(decision) == serialize_current_phase_decision(baseline)


def test_transition_watch_required_downgrades_confirmed() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(transition_watch_required=True),
        phase_history=[],
    )

    assert decision.decision_status == "transition_watch"
    assert decision.current_phase_id == "recovery"
    assert "transition_watch_required" in decision.details["transition_controls"]["blocked"]
    assert "轉換觀察" in decision.reason_zh


def test_transition_watch_required_allows_confirmed_after_watch() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(transition_watch_required=True),
        phase_history=[{"decision_status": "transition_watch", "candidate_phase_id": "growth"}],
    )

    assert decision.decision_status == "confirmed"
    assert decision.details["transition_controls"]["applied"] == ["transition_watch_required"]
    assert decision.details["transition_controls"]["blocked"] == []


def test_confirmation_period_history_insufficient_downgrades_confirmed() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(confirmation_period=2),
        phase_history=[],
    )

    assert decision.decision_status == "transition_watch"
    assert "confirmation_period" in decision.details["transition_controls"]["blocked"]


def test_hysteresis_margin_blocks_when_margin_too_small() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(hysteresis_margin=10.0),
    )

    assert decision.decision_status == "transition_watch"
    assert "hysteresis_margin" in decision.details["transition_controls"]["blocked"]
    assert "margin" in decision.reason_zh


def test_cooldown_period_blocks_recent_confirmed_transition() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(cooldown_period=2),
        phase_history=[{"decision_status": "confirmed", "candidate_phase_id": "recovery"}],
    )

    assert decision.decision_status == "transition_watch"
    assert "cooldown_period" in decision.details["transition_controls"]["blocked"]


def test_breadth_confirmation_placeholder_records_warning() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(breadth_confirmation=True),
        phase_history=[{"decision_status": "transition_watch", "candidate_phase_id": "growth"}],
    )

    assert decision.decision_status == "confirmed"
    assert "breadth_confirmation" in decision.details["transition_controls"]["applied"]
    assert decision.details["transition_controls"]["warnings"]


def test_controls_do_not_emit_manual_review_required() -> None:
    decision = resolve_current_phase(
        [phase_score("recovery", 70), phase_score("growth", 78)],
        config(),
        previous_phase_id="recovery",
        transition_controls=controls(transition_watch_required=True),
    )

    payload = serialize_current_phase_decision(decision)
    assert "manual_review_required" not in str(payload)


def test_replace_control_helper_smoke() -> None:
    base = controls(enabled=False)
    enabled = replace(base, enabled=True)

    assert enabled.enabled is True
