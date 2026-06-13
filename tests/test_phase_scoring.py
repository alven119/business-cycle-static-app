from __future__ import annotations

import pytest

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.catalog import load_phase_spec
from business_cycle.phases.scoring import score_phase
from business_cycle.phases.specs import PhaseIndicatorWeight, PhaseScoringSpec


def indicator_score(indicator_id: str, score: float, confidence: float = 1.0) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=confidence,
        as_of="2024-12-31",
        method="test",
        reason_zh="測試",
        details={},
    )


def phase_spec(
    *,
    indicators: list[PhaseIndicatorWeight] | None = None,
    minimum_available_weight: float = 0.7,
    confidence_policy: dict | None = None,
    thresholds: dict | None = None,
) -> PhaseScoringSpec:
    return PhaseScoringSpec(
        phase_id="recovery",
        phase_name_zh="復甦期",
        description_zh="測試",
        indicators=indicators
        or [
            PhaseIndicatorWeight("a", 0.5, "core"),
            PhaseIndicatorWeight("b", 0.3, "confirmation"),
            PhaseIndicatorWeight("c", 0.2, "optional"),
        ],
        minimum_available_weight=minimum_available_weight,
        confidence_policy=confidence_policy
        or {
            "missing_core_indicator_penalty": 0.2,
            "missing_optional_indicator_penalty": 0.05,
        },
        early_mid_late_thresholds=thresholds or {"early": 55.0, "mid": 70.0, "late": 82.0},
    )


def test_recovery_phase_can_be_scored() -> None:
    spec = load_phase_spec("specs/phases/recovery.yaml")
    scores = {
        "initial_jobless_claims": indicator_score("initial_jobless_claims", 80),
        "real_retail_sales": indicator_score("real_retail_sales", 75),
        "durable_goods_orders": indicator_score("durable_goods_orders", 70),
        "unemployment_rate": indicator_score("unemployment_rate", 60),
    }

    result = score_phase(spec, scores)

    assert result.phase_id == "recovery"
    assert 0.0 <= result.score <= 100.0
    assert 0.0 <= result.confidence <= 1.0


def test_weighted_average_is_correct() -> None:
    result = score_phase(
        phase_spec(),
        {
            "a": indicator_score("a", 80),
            "b": indicator_score("b", 50),
            "c": indicator_score("c", 20),
        },
    )

    assert result.score == pytest.approx(59.0)
    assert result.details["raw_weighted_score"] == pytest.approx(59.0)


def test_missing_indicator_and_available_weight_are_reported() -> None:
    result = score_phase(
        phase_spec(),
        {
            "a": indicator_score("a", 80),
            "c": indicator_score("c", 20),
        },
    )

    assert result.missing_indicators == ["b"]
    assert result.available_weight == pytest.approx(0.7)


def test_available_weight_below_minimum_reduces_confidence() -> None:
    result = score_phase(
        phase_spec(minimum_available_weight=0.8),
        {"a": indicator_score("a", 90)},
    )

    assert result.available_weight == pytest.approx(0.5)
    assert result.confidence < 0.5
    assert "可用指標權重低於門檻" in result.reason_zh


def test_contributing_indicators_include_expected_fields() -> None:
    result = score_phase(phase_spec(), {"a": indicator_score("a", 80)})

    contribution = result.contributing_indicators[0]
    assert contribution == {
        "indicator_id": "a",
        "original_score": 80,
        "phase_signal_score": 80,
        "confidence": 1.0,
        "weight": 0.5,
        "weighted_contribution": 40.0,
        "role": "core",
        "signal_transform": "as_is",
    }


def test_stage_hint_early_mid_late() -> None:
    spec = phase_spec(indicators=[PhaseIndicatorWeight("a", 1.0, "core")])

    assert score_phase(spec, {"a": indicator_score("a", 60)}).stage_hint == "early"
    assert score_phase(spec, {"a": indicator_score("a", 75)}).stage_hint == "mid"
    assert score_phase(spec, {"a": indicator_score("a", 90)}).stage_hint == "late"


def test_low_indicator_confidence_reduces_phase_confidence() -> None:
    high = score_phase(phase_spec(), {"a": indicator_score("a", 80, confidence=1.0)})
    low = score_phase(phase_spec(), {"a": indicator_score("a", 80, confidence=0.2)})

    assert low.confidence < high.confidence


def test_phase_scoring_does_not_produce_current_phase() -> None:
    result = score_phase(phase_spec(), {"a": indicator_score("a", 80)})

    assert not hasattr(result, "current_phase")


def test_single_high_score_indicator_with_low_available_weight_has_low_confidence() -> None:
    result = score_phase(
        phase_spec(minimum_available_weight=0.8),
        {"c": indicator_score("c", 100, confidence=1.0)},
    )

    assert result.score == 100.0
    assert result.available_weight == pytest.approx(0.2)
    assert result.confidence < 0.2


def test_missing_optional_penalty_is_smaller_than_missing_core_penalty() -> None:
    spec = phase_spec(
        indicators=[
            PhaseIndicatorWeight("core", 0.5, "core"),
            PhaseIndicatorWeight("optional", 0.5, "optional"),
        ],
        minimum_available_weight=0.0,
        confidence_policy={
            "missing_core_indicator_penalty": 0.3,
            "missing_optional_indicator_penalty": 0.05,
        },
    )

    missing_core = score_phase(spec, {"optional": indicator_score("optional", 70)})
    missing_optional = score_phase(spec, {"core": indicator_score("core", 70)})

    assert missing_core.confidence < missing_optional.confidence


def test_unlisted_indicator_score_is_ignored() -> None:
    without_extra = score_phase(phase_spec(), {"a": indicator_score("a", 80)})
    with_extra = score_phase(
        phase_spec(),
        {
            "a": indicator_score("a", 80),
            "unlisted": indicator_score("unlisted", 0),
        },
    )

    assert with_extra.score == without_extra.score
    assert with_extra.confidence == without_extra.confidence


def test_details_include_required_fields() -> None:
    result = score_phase(phase_spec(), {"a": indicator_score("a", 80)}, as_of="2024-12-31")

    assert result.details["available_weight"] == pytest.approx(0.5)
    assert result.details["minimum_available_weight"] == pytest.approx(0.7)
    assert result.details["missing_indicators"] == ["b", "c"]
    assert result.details["confidence_policy"]
    assert result.details["stage_thresholds"] == {"early": 55.0, "mid": 70.0, "late": 82.0}
    assert result.details["signal_transforms"] == {"a": "as_is", "b": "as_is", "c": "as_is"}
    assert result.details["as_of"] == "2024-12-31"


def test_as_is_uses_original_indicator_score() -> None:
    spec = phase_spec(indicators=[PhaseIndicatorWeight("a", 1.0, "core", signal_transform="as_is")])

    result = score_phase(spec, {"a": indicator_score("a", 82)})

    assert result.score == 82.0
    assert result.contributing_indicators[0]["original_score"] == 82
    assert result.contributing_indicators[0]["phase_signal_score"] == 82


def test_inverted_uses_one_hundred_minus_original_score() -> None:
    spec = phase_spec(indicators=[PhaseIndicatorWeight("a", 1.0, "core", signal_transform="inverted")])

    result = score_phase(spec, {"a": indicator_score("a", 20)})

    assert result.score == 80.0
    assert result.contributing_indicators[0]["original_score"] == 20
    assert result.contributing_indicators[0]["phase_signal_score"] == 80.0
    assert result.contributing_indicators[0]["signal_transform"] == "inverted"


def test_weighted_average_uses_phase_signal_score_not_original_score() -> None:
    spec = phase_spec(
        indicators=[
            PhaseIndicatorWeight("a", 0.5, "core", signal_transform="as_is"),
            PhaseIndicatorWeight("b", 0.5, "core", signal_transform="inverted"),
        ]
    )

    result = score_phase(
        spec,
        {
            "a": indicator_score("a", 80),
            "b": indicator_score("b", 20),
        },
    )

    assert result.score == 80.0


def test_recovery_existing_behavior_is_unchanged_with_as_is() -> None:
    spec = load_phase_spec("specs/phases/recovery.yaml")
    scores = {
        "initial_jobless_claims": indicator_score("initial_jobless_claims", 80),
        "real_retail_sales": indicator_score("real_retail_sales", 75),
        "durable_goods_orders": indicator_score("durable_goods_orders", 70),
        "unemployment_rate": indicator_score("unemployment_rate", 60),
    }

    result = score_phase(spec, scores)

    assert result.score == pytest.approx(73.0)
    assert {item["signal_transform"] for item in result.contributing_indicators} == {"as_is"}
