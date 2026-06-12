from __future__ import annotations

import math

import pandas as pd

from business_cycle.indicators.scoring import (
    IndicatorScoreResult,
    level_percentile_score,
    moving_average_slope_score,
    peak_trough_reversal_score,
    yoy_momentum_score,
)


def monthly_frame(values: list[float | int | str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )


def assert_valid_result(result: IndicatorScoreResult) -> None:
    assert 0.0 <= result.score <= 100.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.indicator_id
    assert result.method
    assert result.reason_zh


def test_all_scores_and_confidence_are_bounded() -> None:
    results = [
        level_percentile_score(
            monthly_frame([1, 2, 3, 4, 5]),
            indicator_id="x",
            direction="higher_is_better",
            min_periods=3,
        ),
        moving_average_slope_score(
            monthly_frame([1, 2, 3, 4, 5, 6, 7]),
            indicator_id="x",
            direction="rising_is_better",
        ),
        yoy_momentum_score(
            monthly_frame([100, 101, 102, 103, 110, 118, 127]),
            indicator_id="x",
            direction="higher_is_better",
            periods=3,
            momentum_window=2,
        ),
        peak_trough_reversal_score(
            monthly_frame([5, 4, 3, 4, 5, 6]),
            indicator_id="x",
            mode="trough_recovery",
            lookback_window=3,
            confirmation_window=2,
        ),
    ]

    for result in results:
        assert_valid_result(result)


def test_level_percentile_score_higher_is_better() -> None:
    result = level_percentile_score(
        monthly_frame([1, 2, 3, 4, 5]),
        indicator_id="retail",
        direction="higher_is_better",
        min_periods=3,
    )

    assert result.score > 80
    assert result.confidence == 1.0


def test_level_percentile_score_lower_is_better() -> None:
    result = level_percentile_score(
        monthly_frame([1, 2, 3, 4, 5]),
        indicator_id="claims",
        direction="lower_is_better",
        min_periods=3,
    )

    assert result.score < 20
    assert result.confidence == 1.0


def test_moving_average_slope_score_rising_trend_gets_high_score() -> None:
    result = moving_average_slope_score(
        monthly_frame([1, 2, 3, 4, 5, 6, 7, 8]),
        indicator_id="orders",
        direction="rising_is_better",
    )

    assert result.score > 70
    assert result.confidence > 0.8


def test_moving_average_slope_score_falling_trend_gets_low_score() -> None:
    result = moving_average_slope_score(
        monthly_frame([8, 7, 6, 5, 4, 3, 2, 1]),
        indicator_id="orders",
        direction="rising_is_better",
    )

    assert result.score < 30
    assert result.confidence > 0.8


def test_moving_average_slope_score_flat_trend_is_near_neutral() -> None:
    result = moving_average_slope_score(
        monthly_frame([4, 4, 4, 4, 4, 4, 4, 4]),
        indicator_id="rate",
        direction="rising_is_better",
    )

    assert result.score == 50.0
    assert result.confidence > 0.8


def test_moving_average_slope_score_single_spike_is_not_sustained_high_score() -> None:
    result = moving_average_slope_score(
        monthly_frame([10, 10, 10, 60, 10, 10, 10, 10]),
        indicator_id="spike",
        direction="rising_is_better",
    )

    assert result.score < 70.0
    assert result.details["recent_slopes"][-1] <= 0


def test_yoy_momentum_score_improving_growth_scores_higher() -> None:
    improving = yoy_momentum_score(
        monthly_frame([100, 100, 100, 100, 105, 111, 118, 126]),
        indicator_id="consumption",
        direction="higher_is_better",
        periods=3,
        momentum_window=2,
    )
    flat = yoy_momentum_score(
        monthly_frame([100, 100, 100, 100, 101, 102, 103, 104]),
        indicator_id="consumption",
        direction="higher_is_better",
        periods=3,
        momentum_window=2,
    )

    assert improving.score > flat.score
    assert improving.score > 60


def test_yoy_momentum_score_deteriorating_growth_scores_lower() -> None:
    result = yoy_momentum_score(
        monthly_frame([100, 110, 121, 133, 130, 126, 121, 115]),
        indicator_id="production",
        direction="higher_is_better",
        periods=3,
        momentum_window=2,
    )

    assert result.score < 50


def test_peak_trough_reversal_score_requires_confirmation_window() -> None:
    unconfirmed = peak_trough_reversal_score(
        monthly_frame([5, 4, 3, 4]),
        indicator_id="claims",
        mode="trough_recovery",
        lookback_window=3,
        confirmation_window=2,
    )
    confirmed = peak_trough_reversal_score(
        monthly_frame([5, 4, 3, 4, 5]),
        indicator_id="claims",
        mode="trough_recovery",
        lookback_window=3,
        confirmation_window=2,
    )

    assert unconfirmed.score == 50.0
    assert unconfirmed.details["confirmed"] is False
    assert confirmed.score > unconfirmed.score
    assert confirmed.details["confirmed"] is True


def test_insufficient_history_reduces_confidence() -> None:
    result = level_percentile_score(
        monthly_frame([1, 2]),
        indicator_id="short",
        direction="higher_is_better",
        min_periods=12,
    )

    assert result.confidence < 0.3


def test_missing_values_do_not_crash_and_reduce_confidence() -> None:
    result = moving_average_slope_score(
        monthly_frame([1, 2, ".", 4, 5, 6, 7]),
        indicator_id="missing",
        direction="rising_is_better",
    )

    assert_valid_result(result)
    assert result.confidence < 1.0


def test_scoring_does_not_use_future_data() -> None:
    prefix = monthly_frame([1, 2, 3, 4, 5, 6])
    with_future = monthly_frame([1, 2, 3, 4, 5, 6, 1000, 2000])

    first = moving_average_slope_score(
        prefix,
        indicator_id="orders",
        direction="rising_is_better",
        as_of="2020-06-01",
    )
    second = moving_average_slope_score(
        with_future,
        indicator_id="orders",
        direction="rising_is_better",
        as_of="2020-06-01",
    )

    assert second.score == first.score
    assert second.confidence == first.confidence
    assert second.as_of == first.as_of


def test_stale_data_reduces_confidence() -> None:
    result = level_percentile_score(
        monthly_frame([1, 2, 3, 4]),
        indicator_id="stale",
        direction="higher_is_better",
        min_periods=3,
        stale_after_days=30,
        as_of="2021-01-01",
    )

    assert math.isclose(result.confidence, 0.5)
