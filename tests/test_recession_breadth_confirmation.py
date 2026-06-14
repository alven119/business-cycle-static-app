from __future__ import annotations

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
    load_transition_controls_config,
)

BREADTH_CONFIG_PATH = "specs/backtests/transition_controls_recession_breadth_experiment.yaml"


def config() -> PhaseStateMachineConfig:
    return PhaseStateMachineConfig(
        phase_order=["recovery", "growth", "boom", "recession"],
        min_phase_confidence=0.65,
        min_available_weight=0.70,
        min_score_for_initial_estimate=55.0,
        min_score_margin=8.0,
        transition_score_margin=5.0,
        allow_initial_estimate=True,
    )


def phase_score(phase_id: str, score: float, contributions: list[dict] | None = None) -> PhaseScoreResult:
    return PhaseScoreResult(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        score=score,
        confidence=0.9,
        available_weight=1.0,
        missing_indicators=[],
        contributing_indicators=contributions or [],
        stage_hint=None,
        reason_zh="synthetic",
        details={},
    )


def contribution(indicator_id: str, score: float = 70.0, confidence: float = 0.9) -> dict:
    return {
        "indicator_id": indicator_id,
        "phase_signal_score": score,
        "confidence": confidence,
        "weight": 0.1,
        "weighted_contribution": 7.0,
        "role": "core",
    }


def controls(*, enabled: bool = True, breadth_enabled: bool = True) -> TransitionControlsConfig:
    return TransitionControlsConfig(
        version=1,
        enabled=enabled,
        description_zh="test",
        transition_watch_required=TransitionWatchRequiredControl(enabled=False),
        confirmation_period=ConfirmationPeriodControl(enabled=False),
        hysteresis_margin=HysteresisMarginControl(enabled=False),
        cooldown_period=CooldownPeriodControl(enabled=False),
        breadth_confirmation=BreadthConfirmationControl(
            enabled=breadth_enabled,
            target_phases=["recession"],
            min_group_count=3,
            min_core_group_count=2,
            min_indicator_count=4,
            min_phase_signal_score=55.0,
            min_indicator_confidence=0.5,
            allowed_groups=[
                "employment",
                "consumption",
                "investment",
                "trade",
                "rates_financial_conditions",
                "commodities",
            ],
        ),
        caveats_zh=["使用修訂後歷史資料。", "不構成投資建議。"],
    )


def resolve_with_contributions(contributions: list[dict], transition_controls=None):
    return resolve_current_phase(
        [
            phase_score("boom", 60.0),
            phase_score("recession", 72.0, contributions),
        ],
        config(),
        previous_phase_id="boom",
        transition_controls=transition_controls,
    )


def test_breadth_config_can_be_loaded() -> None:
    loaded = load_transition_controls_config(BREADTH_CONFIG_PATH)

    assert loaded.enabled is True
    assert loaded.breadth_confirmation.enabled is True
    assert loaded.breadth_confirmation.target_phases == ["recession"]
    assert loaded.breadth_confirmation.min_group_count == 3
    assert loaded.breadth_confirmation.min_indicator_count == 4


def test_controls_none_keeps_baseline_result() -> None:
    baseline = resolve_with_contributions([contribution("initial_jobless_claims")])
    decision = resolve_with_contributions([contribution("initial_jobless_claims")], transition_controls=None)

    assert serialize_current_phase_decision(decision) == serialize_current_phase_decision(baseline)
    assert decision.decision_status == "confirmed"


def test_breadth_disabled_keeps_phase_7b_behavior() -> None:
    baseline = resolve_with_contributions([contribution("initial_jobless_claims")])
    decision = resolve_with_contributions(
        [contribution("initial_jobless_claims")],
        transition_controls=controls(breadth_enabled=False),
    )

    assert decision.decision_status == baseline.decision_status
    assert "breadth_confirmation" not in decision.details["transition_controls"]["blocked"]


def test_employment_only_support_blocks_confirmed_recession() -> None:
    decision = resolve_with_contributions(
        [
            contribution("initial_jobless_claims"),
            contribution("short_term_unemployment"),
            contribution("unemployment_rate"),
        ],
        transition_controls=controls(),
    )

    assert decision.decision_status == "transition_watch"
    assert decision.current_phase_id == "boom"
    details = decision.details["transition_controls"]
    assert "breadth_confirmation" in details["blocked"]
    assert details["breadth_summary"]["supported_groups"] == ["employment"]
    assert details["breadth_summary"]["supported_indicator_count"] == 3
    assert "多指標群組同步確認門檻" in decision.reason_zh


def test_employment_consumption_investment_support_allows_confirmed_recession() -> None:
    decision = resolve_with_contributions(
        [
            contribution("initial_jobless_claims"),
            contribution("short_term_unemployment"),
            contribution("real_retail_sales"),
            contribution("durable_goods_orders"),
        ],
        transition_controls=controls(),
    )

    assert decision.decision_status == "confirmed"
    details = decision.details["transition_controls"]
    assert "breadth_confirmation" in details["applied"]
    assert details["blocked"] == []
    assert details["breadth_summary"]["passed"] is True
    assert details["breadth_summary"]["supported_groups"] == ["consumption", "employment", "investment"]
    assert details["breadth_summary"]["supported_core_group_count"] == 3


def test_insufficient_evidence_blocks_confirmed_recession_without_crashing() -> None:
    decision = resolve_with_contributions([], transition_controls=controls())

    assert decision.decision_status == "transition_watch"
    details = decision.details["transition_controls"]
    assert "breadth_confirmation" in details["blocked"]
    assert "breadth_confirmation_insufficient_evidence" in details["warnings"]
    assert details["breadth_summary"]["insufficient_evidence"] is True


def test_low_score_or_confidence_indicator_not_counted() -> None:
    decision = resolve_with_contributions(
        [
            contribution("initial_jobless_claims", score=54.0),
            contribution("short_term_unemployment"),
            contribution("real_retail_sales", confidence=0.49),
            contribution("durable_goods_orders"),
            contribution("real_private_fixed_investment"),
        ],
        transition_controls=controls(),
    )

    summary = decision.details["transition_controls"]["breadth_summary"]
    assert decision.decision_status == "transition_watch"
    assert summary["supported_groups"] == ["employment", "investment"]
    assert summary["supported_indicator_count"] == 3


def test_breadth_confirmation_does_not_emit_manual_review_required() -> None:
    decision = resolve_with_contributions([], transition_controls=controls())

    assert "manual_review_required" not in str(serialize_current_phase_decision(decision))
