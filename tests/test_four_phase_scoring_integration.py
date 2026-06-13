from __future__ import annotations

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.batch_scoring import score_phase_batch_safe
from business_cycle.phases.catalog import load_phase_specs


def indicator_score(indicator_id: str, score: float, confidence: float = 0.90) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=confidence,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def test_four_mvp_phase_specs_can_be_scored_with_synthetic_indicator_scores() -> None:
    phase_specs = load_phase_specs("specs/phases")
    indicator_scores = {
        "unemployment_rate": indicator_score("unemployment_rate", 78),
        "initial_jobless_claims": indicator_score("initial_jobless_claims", 82),
        "short_term_unemployment": indicator_score("short_term_unemployment", 76),
        "real_retail_sales": indicator_score("real_retail_sales", 80),
        "real_pce_durable_goods": indicator_score("real_pce_durable_goods", 74),
        "durable_goods_orders": indicator_score("durable_goods_orders", 72),
        "real_private_fixed_investment": indicator_score("real_private_fixed_investment", 70),
        "imports_goods_services": indicator_score("imports_goods_services", 68),
        "exports_goods_services": indicator_score("exports_goods_services", 66),
        "federal_funds_rate": indicator_score("federal_funds_rate", 64),
        "ten_year_treasury_yield": indicator_score("ten_year_treasury_yield", 62),
        "thirty_year_mortgage_rate": indicator_score("thirty_year_mortgage_rate", 58),
        "wti_oil_price": indicator_score("wti_oil_price", 60),
    }

    summary = score_phase_batch_safe(phase_specs, indicator_scores)

    assert summary.total_phases == 4
    assert summary.scored_phases == 4
    assert summary.failed_phases == 0
    assert {result.phase_id for result in summary.results} == {
        "recovery",
        "growth",
        "boom",
        "recession",
    }
    for result in summary.results:
        assert 0.0 <= result.score <= 100.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.available_weight > 0.0
        assert not hasattr(result, "current_phase")

    recession = next(result for result in summary.results if result.phase_id == "recession")
    recession_retail = next(
        indicator
        for indicator in recession.contributing_indicators
        if indicator["indicator_id"] == "real_retail_sales"
    )
    assert recession_retail["signal_transform"] == "inverted"
    assert recession_retail["original_score"] == 80
    assert recession_retail["phase_signal_score"] == 20
