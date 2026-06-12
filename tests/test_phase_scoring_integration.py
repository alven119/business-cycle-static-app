from __future__ import annotations

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.catalog import load_phase_spec
from business_cycle.phases.scoring import score_phase
from business_cycle.phases.specs import PhaseScoreResult


def indicator_score(indicator_id: str, score: float, confidence: float) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=confidence,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def test_recovery_phase_scoring_with_synthetic_indicator_scores() -> None:
    phase_spec = load_phase_spec("specs/phases/recovery.yaml")
    indicator_scores = {
        "initial_jobless_claims": indicator_score("initial_jobless_claims", 82, 0.90),
        "real_retail_sales": indicator_score("real_retail_sales", 78, 0.85),
        "durable_goods_orders": indicator_score("durable_goods_orders", 72, 0.80),
        "unemployment_rate": indicator_score("unemployment_rate", 60, 0.75),
    }

    result = score_phase(phase_spec, indicator_scores)

    assert isinstance(result, PhaseScoreResult)
    assert result.phase_id == "recovery"
    assert 0.0 <= result.score <= 100.0
    assert result.score > 70.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence > 0.75
    assert result.available_weight == 1.0
    assert result.stage_hint in {"mid", "late"}
    assert result.missing_indicators == []
    assert not hasattr(result, "current_phase")

