from __future__ import annotations

import pandas as pd

from business_cycle.indicators.experimental import (
    commodity_pressure_score,
    credit_spread_widening_score,
    labor_market_late_cycle_pressure_score,
    production_momentum_loss_score,
    restrictive_policy_pressure_score,
    yield_curve_inversion_pressure_score,
)


def test_yield_curve_sustained_inversion_scores_high() -> None:
    frame = monthly_series([1.2] * 70 + [-0.5] * 20)

    score = yield_curve_inversion_pressure_score(frame, as_of="2022-06-30")

    assert score.score is not None
    assert score.score >= 70
    assert score.confidence >= 0.5


def test_yield_curve_single_inversion_has_low_confidence() -> None:
    frame = monthly_series([1.2] * 89 + [-0.2])

    score = yield_curve_inversion_pressure_score(frame, as_of="2022-06-30")

    assert score.confidence < 0.5


def test_policy_rate_sustained_increase_scores_restrictive() -> None:
    frame = monthly_series([0.5 + i * 0.05 for i in range(120)])

    score = restrictive_policy_pressure_score(frame, as_of="2022-12-31")

    assert score.score is not None
    assert score.score >= 65


def test_credit_spread_widening_scores_high() -> None:
    frame = monthly_series([1.0] * 80 + [1.1 + i * 0.05 for i in range(40)])

    score = credit_spread_widening_score(frame, as_of="2022-12-31")

    assert score.score is not None
    assert score.score >= 65


def test_oil_price_one_off_spike_does_not_have_high_confidence() -> None:
    frame = weekly_series([70.0] * 130 + [120.0])

    score = commodity_pressure_score(frame, as_of="2022-07-01")

    assert score.confidence < 0.7


def test_unemployment_rate_low_but_not_rising_does_not_score_high() -> None:
    frame = monthly_series([5.0] * 60 + [3.6] * 60)

    score = labor_market_late_cycle_pressure_score(frame, as_of="2022-12-31")

    assert score.score is not None
    assert score.score <= 45


def test_production_momentum_loss_scores_high() -> None:
    frame = monthly_series([100 + i * 0.4 for i in range(80)] + [132 - i * 0.5 for i in range(40)])

    score = production_momentum_loss_score(frame, as_of="2022-12-31")

    assert score.score is not None
    assert score.score >= 60


def test_boom_ending_scoring_insufficient_data_lowers_confidence() -> None:
    frame = monthly_series([1.0, 0.9, 0.8])

    score = yield_curve_inversion_pressure_score(frame, as_of="2010-03-31")

    assert score.confidence < 0.4


def monthly_series(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2015-01-31", periods=len(values), freq="ME"),
            "value": values,
        }
    )


def weekly_series(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-03", periods=len(values), freq="W-FRI"),
            "value": values,
        }
    )
