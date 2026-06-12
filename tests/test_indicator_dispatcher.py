from __future__ import annotations

import pandas as pd
import pytest

from business_cycle.indicators.dispatcher import IndicatorScoringError, score_indicator
from business_cycle.indicators.specs import IndicatorScoringSpec


def monthly_frame(values: list[float | int | str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )


def assert_bounded(result) -> None:  # noqa: ANN001
    assert 0.0 <= result.score <= 100.0
    assert 0.0 <= result.confidence <= 1.0


def test_dispatcher_calls_level_percentile_score() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="retail",
        score_method="level_percentile_score",
        direction="higher_is_better",
        parameters={"min_periods": 3},
    )

    result = score_indicator(monthly_frame([1, 2, 3, 4]), spec)

    assert result.method == "level_percentile_score"
    assert result.score > 80
    assert result.details["dispatcher"]["method"] == "level_percentile_score"
    assert result.details["dispatcher"]["available_observations"] == 4
    assert_bounded(result)


def test_dispatcher_calls_moving_average_slope_score() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="orders",
        score_method="moving_average_slope_score",
        direction="rising_is_better",
        parameters={"moving_average_window": 2, "slope_window": 3, "confirmation_window": 2},
    )

    result = score_indicator(monthly_frame([1, 2, 3, 4, 5, 6]), spec)

    assert result.method == "moving_average_slope_score"
    assert result.score > 70
    assert_bounded(result)


def test_dispatcher_calls_yoy_momentum_score() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="consumption",
        score_method="yoy_momentum_score",
        direction="higher_is_better",
        parameters={"periods": 3, "momentum_window": 2},
    )

    result = score_indicator(monthly_frame([100, 100, 100, 105, 111, 118, 126]), spec)

    assert result.method == "yoy_momentum_score"
    assert result.score > 60
    assert_bounded(result)


def test_dispatcher_calls_peak_trough_reversal_score() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="claims",
        score_method="peak_trough_reversal_score",
        direction="lower_is_better",
        parameters={"mode": "trough_recovery", "lookback_window": 3, "confirmation_window": 2},
    )

    result = score_indicator(monthly_frame([5, 4, 3, 4, 5]), spec)

    assert result.method == "peak_trough_reversal_score"
    assert result.details["confirmed"] is True
    assert_bounded(result)


def test_unsupported_score_method_raises_clear_error() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="x",
        score_method="unknown_score",
        direction="higher_is_better",
    )

    with pytest.raises(IndicatorScoringError, match="Unsupported score_method"):
        score_indicator(monthly_frame([1, 2, 3]), spec)


def test_missing_required_parameter_raises_clear_error() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="x",
        score_method="yoy_momentum_score",
        direction="higher_is_better",
        parameters={"momentum_window": 2},
    )

    with pytest.raises(IndicatorScoringError, match="missing required parameter"):
        score_indicator(monthly_frame([1, 2, 3, 4]), spec)


def test_as_of_filters_future_data() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="orders",
        score_method="moving_average_slope_score",
        direction="rising_is_better",
        parameters={"moving_average_window": 2, "slope_window": 3, "confirmation_window": 2},
    )
    prefix = monthly_frame([1, 2, 3, 4, 5, 6])
    with_future = monthly_frame([1, 2, 3, 4, 5, 6, 100, 200])

    first = score_indicator(prefix, spec, as_of="2020-06-01")
    second = score_indicator(with_future, spec, as_of="2020-06-01")

    assert second.score == first.score
    assert second.confidence == first.confidence
    assert second.as_of == "2020-06-01"
    assert second.details["dispatcher"]["available_observations"] == 6


def test_stale_data_reduces_confidence() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="stale",
        score_method="level_percentile_score",
        direction="higher_is_better",
        parameters={"min_periods": 3},
        stale_after_days=30,
    )

    result = score_indicator(monthly_frame([1, 2, 3]), spec, as_of="2021-01-01")

    assert result.confidence == 0.5


def test_missing_values_do_not_crash() -> None:
    spec = IndicatorScoringSpec(
        indicator_id="missing",
        score_method="moving_average_slope_score",
        direction="higher_is_stronger",
        parameters={"moving_average_window": 2, "slope_window": 3, "confirmation_window": 2},
    )

    result = score_indicator(monthly_frame([1, ".", 3, 4, 5]), spec)

    assert_bounded(result)
    assert result.confidence < 1.0


def test_custom_date_and_value_columns_are_supported() -> None:
    observations = pd.DataFrame(
        {
            "observation_date": pd.date_range("2020-01-01", periods=4, freq="MS"),
            "raw_value": [1, 2, 3, 4],
        }
    )
    spec = IndicatorScoringSpec(
        indicator_id="custom",
        score_method="level_percentile_score",
        direction="higher_is_better",
        date_column="observation_date",
        value_column="raw_value",
        parameters={"min_periods": 3},
    )

    result = score_indicator(observations, spec)

    assert result.score > 80
    assert_bounded(result)

