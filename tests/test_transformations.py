from __future__ import annotations

import math

import pandas as pd
import pytest

from business_cycle.indicators.transformations import (
    add_moving_average,
    add_pct_change,
    add_rolling_percentile,
    add_rolling_slope,
    add_rolling_zscore,
    clean_observations,
    detect_peak_trough,
)


def frame(values: list[float | int | str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )


def test_clean_observations_sorts_dates_and_converts_values() -> None:
    raw = pd.DataFrame(
        {
            "date": ["2024-03-01", "not-a-date", "2024-01-01", "2024-02-01"],
            "value": ["3.5", "100", ".", "2"],
        }
    )

    cleaned = clean_observations(raw)

    assert cleaned["date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2024-01-01",
        "2024-02-01",
        "2024-03-01",
    ]
    assert math.isnan(cleaned.loc[0, "value"])
    assert cleaned["value"].tolist()[1:] == [2.0, 3.5]


def test_add_moving_average_uses_trailing_window() -> None:
    result = add_moving_average(frame([1, 2, 3, 4]), window=3, output_column="ma")

    assert math.isnan(result.loc[0, "ma"])
    assert math.isnan(result.loc[1, "ma"])
    assert result["ma"].tolist()[2:] == [2.0, 3.0]


def test_add_pct_change_supports_periods() -> None:
    result = add_pct_change(frame([100, 110, 121]), periods=1, output_column="pct")

    assert math.isnan(result.loc[0, "pct"])
    assert result.loc[1, "pct"] == pytest.approx(0.10)
    assert result.loc[2, "pct"] == pytest.approx(0.10)


def test_rolling_slope_positive_for_rising_trend() -> None:
    result = add_rolling_slope(frame([1, 2, 3, 4, 5]), window=3, output_column="slope")

    assert result.loc[2, "slope"] > 0
    assert result.loc[4, "slope"] == pytest.approx(1.0)


def test_rolling_slope_negative_for_falling_trend() -> None:
    result = add_rolling_slope(frame([5, 4, 3, 2, 1]), window=3, output_column="slope")

    assert result.loc[2, "slope"] < 0
    assert result.loc[4, "slope"] == pytest.approx(-1.0)


def test_rolling_slope_flat_trend_is_near_zero() -> None:
    result = add_rolling_slope(frame([3, 3, 3, 3]), window=3, output_column="slope")

    assert result.loc[2, "slope"] == pytest.approx(0.0)
    assert result.loc[3, "slope"] == pytest.approx(0.0)


def test_rolling_zscore_std_zero_is_nan() -> None:
    result = add_rolling_zscore(frame([2, 2, 2]), window=3, output_column="z")

    assert math.isnan(result.loc[2, "z"])


def test_rolling_percentile_range_is_zero_to_one() -> None:
    result = add_rolling_percentile(frame([1, 3, 2, 4]), window=3, output_column="pctile")
    values = result["pctile"].dropna()

    assert not values.empty
    assert values.between(0.0, 1.0).all()


def test_peak_trough_uses_only_past_and_current_data() -> None:
    result = detect_peak_trough(
        frame([1, 3, 2, 5]),
        lookback_window=3,
    )

    assert result.loc[1, "is_local_peak"].item() is False
    assert result.loc[2, "is_local_peak"].item() is False
    assert result.loc[2, "is_local_trough"].item() is False
    assert result.loc[3, "is_local_peak"].item() is True


def test_insufficient_data_does_not_create_fake_trends() -> None:
    values = frame([1, 2])

    slope = add_rolling_slope(values, window=3, output_column="slope")
    zscore = add_rolling_zscore(values, window=3, output_column="z")
    percentile = add_rolling_percentile(values, window=3, output_column="pctile")
    peaks = detect_peak_trough(values, lookback_window=3)

    assert slope["slope"].isna().all()
    assert zscore["z"].isna().all()
    assert percentile["pctile"].isna().all()
    assert not peaks["is_local_peak"].any()
    assert not peaks["is_local_trough"].any()


def test_one_period_spike_is_not_persistent_trend() -> None:
    result = add_rolling_slope(frame([10, 10, 50, 10, 10]), window=3, output_column="slope")

    assert result.loc[2, "slope"] > 0
    assert result.loc[4, "slope"] < 0
    assert not result["slope"].dropna().gt(0).all()
    assert not result["slope"].dropna().lt(0).all()


def test_transformations_preserve_nan_without_silent_trend() -> None:
    result = add_rolling_slope(frame([1, float("nan"), 3]), window=3, output_column="slope")

    assert math.isnan(result.loc[2, "slope"])
