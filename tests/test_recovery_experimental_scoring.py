from __future__ import annotations

import pandas as pd

from business_cycle.indicators.experimental import (
    bottoming_momentum_score,
    credit_stress_easing_score,
    financial_stress_easing_score,
    peak_reversal_score,
    policy_easing_support_score,
)


def test_claims_sustained_decline_from_peak_scores_high() -> None:
    frame = weekly_series([220.0] * 40 + [520.0] * 8 + [500.0, 460.0, 420.0, 380.0, 340.0, 300.0])

    score = peak_reversal_score(frame, as_of="2021-01-01")

    assert score.score is not None
    assert score.score >= 65
    assert score.confidence >= 0.5
    assert score.metadata["drawdown_from_peak"] > 0


def test_single_period_decline_from_peak_does_not_have_high_confidence() -> None:
    frame = weekly_series([220.0] * 40 + [520.0] * 8 + [500.0])

    score = peak_reversal_score(frame, as_of="2020-12-04")

    assert score.confidence < 0.5


def test_retail_sales_bottoming_scores_high_after_sustained_rebound() -> None:
    frame = monthly_series([110.0] * 30 + [100.0, 96.0, 92.0, 94.0, 97.0, 101.0, 105.0])

    score = bottoming_momentum_score(frame, as_of="2021-01-31")

    assert score.score is not None
    assert score.score >= 65
    assert score.confidence >= 0.5
    assert score.metadata["rebound_from_trough"] > 0


def test_pce_bottoming_scores_high_after_rebound() -> None:
    frame = monthly_series([120.0] * 30 + [112.0, 108.0, 104.0, 106.0, 110.0, 114.0, 118.0])

    score = bottoming_momentum_score(frame, indicator_id="real_pce_bottoming", as_of="2021-01-31")

    assert score.score is not None
    assert score.score >= 65


def test_industrial_production_rebound_scoring() -> None:
    frame = monthly_series([100.0] * 30 + [95.0, 90.0, 86.0, 88.0, 91.0, 94.0, 97.0])

    score = bottoming_momentum_score(frame, indicator_id="industrial_production_bottoming", as_of="2021-01-31")

    assert score.score is not None
    assert score.score >= 65


def test_credit_spread_easing_scores_high() -> None:
    frame = monthly_series([1.0] * 40 + [4.0, 4.2, 4.1, 3.6, 3.0, 2.4, 1.9])

    score = credit_stress_easing_score(frame, as_of="2021-01-31")

    assert score.score is not None
    assert score.score >= 65
    assert "壓力緩解" in score.reason_zh


def test_financial_stress_easing_scores_high() -> None:
    frame = weekly_series([0.0] * 70 + [5.0, 5.2, 4.7, 4.0, 3.2, 2.4, 1.5, 0.8])

    score = financial_stress_easing_score(frame, as_of="2021-06-25")

    assert score.score is not None
    assert score.score >= 65


def test_fed_easing_support_detects_rate_cuts_but_not_confirmed_recovery() -> None:
    frame = monthly_series([5.0] * 30 + [4.5, 4.0, 3.25, 2.5, 1.75, 1.0, 0.5])

    score = policy_easing_support_score(frame, as_of="2021-01-31")

    assert score.score is not None
    assert score.score >= 65
    assert score.metadata["standalone_recovery_confirmation"] is False


def test_recovery_scoring_insufficient_data_lowers_confidence() -> None:
    frame = monthly_series([100.0, 95.0, 97.0])

    score = bottoming_momentum_score(frame, as_of="2015-03-31")

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
