from business_cycle.phases.state_machine import (
    PhaseEvidence,
    TransitionThresholds,
    decide_phase_transition,
    next_phase_for,
)


def test_cycle_order_next_phase() -> None:
    assert next_phase_for("recession") == "recovery"
    assert next_phase_for("recovery") == "growth"
    assert next_phase_for("growth") == "boom"
    assert next_phase_for("boom") == "recession"


def test_can_keep_current_phase_when_score_is_too_low() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recession",
            target_phase="recovery",
            phase_scores={"recovery": 0.50},
            confidence=0.80,
            available_weight=0.90,
            persistence_observations=3,
        )
    )

    assert decision.current_phase == "recession"
    assert decision.transitioned is False
    assert "target_phase_score_below_threshold" in decision.blocked_reasons


def test_can_transition_to_next_phase_when_all_thresholds_pass() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recession",
            target_phase="recovery",
            phase_scores={"recovery": 0.75},
            confidence=0.80,
            available_weight=0.90,
            persistence_observations=3,
            top_positive_reasons=["labor leading indicators improved"],
        )
    )

    assert decision.current_phase == "recovery"
    assert decision.current_substage == "early"
    assert decision.transitioned is True
    assert decision.transition_radar == "confirmed"
    assert decision.top_positive_reasons == ["labor leading indicators improved"]


def test_cannot_skip_phase() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recession",
            target_phase="growth",
            phase_scores={"growth": 0.90},
            confidence=0.90,
            available_weight=0.90,
            persistence_observations=4,
        )
    )

    assert decision.current_phase == "recession"
    assert decision.transitioned is False
    assert "phase_jump_not_allowed" in decision.blocked_reasons


def test_cannot_reverse_phase() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="growth",
            target_phase="recovery",
            phase_scores={"recovery": 0.90},
            confidence=0.90,
            available_weight=0.90,
            persistence_observations=4,
        )
    )

    assert decision.current_phase == "growth"
    assert decision.transitioned is False
    assert "reverse_transition_not_allowed" in decision.blocked_reasons


def test_confidence_too_low_blocks_transition() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recovery",
            target_phase="growth",
            phase_scores={"growth": 0.80},
            confidence=0.40,
            available_weight=0.90,
            persistence_observations=3,
        )
    )

    assert decision.current_phase == "recovery"
    assert decision.transitioned is False
    assert "confidence_below_threshold" in decision.blocked_reasons


def test_available_weight_too_low_blocks_transition() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recovery",
            target_phase="growth",
            phase_scores={"growth": 0.80},
            confidence=0.80,
            available_weight=0.40,
            persistence_observations=3,
        )
    )

    assert decision.current_phase == "recovery"
    assert decision.transitioned is False
    assert "available_weight_below_threshold" in decision.blocked_reasons


def test_persistence_too_low_blocks_transition() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="growth",
            target_phase="boom",
            phase_scores={"boom": 0.80},
            confidence=0.80,
            available_weight=0.80,
            persistence_observations=1,
        )
    )

    assert decision.current_phase == "growth"
    assert decision.transitioned is False
    assert "persistence_below_threshold" in decision.blocked_reasons


def test_mixed_evidence_keeps_phase_and_raises_radar() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="recession",
            target_phase="recovery",
            phase_scores={"recovery": 0.80},
            confidence=0.80,
            available_weight=0.90,
            persistence_observations=3,
            mixed_evidence=True,
            top_positive_reasons=["claims improved"],
            top_warning_reasons=["retail demand still weak"],
        )
    )

    assert decision.current_phase == "recession"
    assert decision.transitioned is False
    assert decision.transition_radar == "elevated"
    assert "mixed_evidence_keeps_current_phase" in decision.blocked_reasons
    assert decision.top_warning_reasons == ["retail demand still weak"]


def test_missing_data_impact_is_reported() -> None:
    decision = decide_phase_transition(
        PhaseEvidence(
            current_phase="boom",
            target_phase="recession",
            phase_scores={"recession": 0.80},
            confidence=0.80,
            available_weight=0.80,
            persistence_observations=3,
            stale_indicators=["real_private_fixed_investment"],
            missing_indicators=["exports_goods_services"],
        ),
        thresholds=TransitionThresholds(),
    )

    assert decision.current_phase == "recession"
    assert decision.missing_data_impact == (
        "missing_indicators=1; stale_indicators=1; "
        "confidence_or_available_weight_should_be_reduced"
    )

