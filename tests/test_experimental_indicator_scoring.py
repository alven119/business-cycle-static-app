from __future__ import annotations

import pandas as pd

from business_cycle.indicators.experimental import (
    credit_stress_score,
    financial_stress_confirmation_score,
    sustained_deterioration_score,
)


def test_sustained_deterioration_scores_persistent_worsening_high() -> None:
    frame = monthly_series([100 + i * 5 for i in range(36)])

    result = sustained_deterioration_score(
        frame,
        indicator_id="continuing_jobless_claims",
        direction="higher_is_worse",
        as_of="2022-12-31",
        yoy_periods=12,
        persistence_window=4,
    )

    assert result.score is not None
    assert result.score > 70
    assert result.confidence >= 0.5
    assert "連續惡化" in result.reason_zh


def test_sustained_deterioration_single_spike_has_lower_confidence() -> None:
    values = [100.0] * 35 + [220.0]
    frame = monthly_series(values)

    result = sustained_deterioration_score(
        frame,
        indicator_id="continuing_jobless_claims",
        direction="higher_is_worse",
        as_of="2022-12-31",
        yoy_periods=12,
        persistence_window=4,
    )

    assert result.score is not None
    assert result.confidence < 0.7
    assert result.metadata["deterioration_share"] < 1.0


def test_sustained_deterioration_insufficient_data_lowers_confidence() -> None:
    frame = monthly_series([100.0, 101.0, 102.0])

    result = sustained_deterioration_score(
        frame,
        indicator_id="continuing_jobless_claims",
        direction="higher_is_worse",
        as_of="2020-03-31",
        yoy_periods=12,
    )

    assert result.score == 50.0
    assert result.confidence < 0.2


def test_credit_spread_score_detects_widening_stress() -> None:
    frame = monthly_series([1.0 + i * 0.05 for i in range(80)])

    result = credit_stress_score(frame, as_of="2026-08-31")

    assert result.score is not None
    assert result.score > 60
    assert result.confidence > 0.5


def test_financial_stress_score_detects_elevated_stress() -> None:
    frame = monthly_series([0.0] * 80 + [0.2, 0.4, 0.8, 1.2, 1.5, 1.8])

    result = financial_stress_confirmation_score(frame, as_of="2027-02-28")

    assert result.score is not None
    assert result.score > 55
    assert result.confidence > 0.3


def monthly_series(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-31", periods=len(values), freq="ME"),
            "value": values,
        }
    )
