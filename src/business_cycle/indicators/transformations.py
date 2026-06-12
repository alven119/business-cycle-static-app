"""Deterministic time-series transformations for macro indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd


def clean_observations(
    frame: pd.DataFrame,
    *,
    date_column: str = "date",
    value_column: str = "value",
) -> pd.DataFrame:
    """Parse date/value columns, drop invalid dates, and sort by date."""

    cleaned = frame.copy()
    cleaned[date_column] = pd.to_datetime(cleaned[date_column], errors="coerce")
    cleaned[value_column] = pd.to_numeric(cleaned[value_column], errors="coerce")
    cleaned = cleaned.dropna(subset=[date_column])
    cleaned = cleaned.sort_values(date_column, kind="mergesort").reset_index(drop=True)
    return cleaned


def add_moving_average(
    frame: pd.DataFrame,
    *,
    window: int,
    value_column: str = "value",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Add a trailing moving average column."""

    _validate_window(window)
    result = frame.copy()
    column = output_column or f"{value_column}_ma_{window}"
    result[column] = result[value_column].rolling(window=window, min_periods=window).mean()
    return result


def add_pct_change(
    frame: pd.DataFrame,
    *,
    periods: int,
    value_column: str = "value",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Add trailing percentage change for MoM, QoQ, YoY, or equivalent periods."""

    if periods <= 0:
        raise ValueError("periods must be positive")
    result = frame.copy()
    column = output_column or f"{value_column}_pct_change_{periods}"
    result[column] = result[value_column].pct_change(periods=periods)
    return result


def add_rolling_slope(
    frame: pd.DataFrame,
    *,
    window: int,
    value_column: str = "value",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Add trailing linear slope estimated over a rolling window."""

    _validate_window(window)
    result = frame.copy()
    column = output_column or f"{value_column}_slope_{window}"
    result[column] = (
        result[value_column]
        .rolling(window=window, min_periods=window)
        .apply(_linear_slope, raw=True)
    )
    return result


def add_rolling_zscore(
    frame: pd.DataFrame,
    *,
    window: int,
    value_column: str = "value",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Add trailing rolling z-score."""

    _validate_window(window)
    result = frame.copy()
    column = output_column or f"{value_column}_zscore_{window}"
    rolling = result[value_column].rolling(window=window, min_periods=window)
    mean = rolling.mean()
    std = rolling.std(ddof=0)
    result[column] = (result[value_column] - mean) / std.replace(0, np.nan)
    return result


def add_rolling_percentile(
    frame: pd.DataFrame,
    *,
    window: int,
    value_column: str = "value",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Add trailing percentile rank of the current value within each rolling window."""

    _validate_window(window)
    result = frame.copy()
    column = output_column or f"{value_column}_percentile_{window}"
    result[column] = (
        result[value_column]
        .rolling(window=window, min_periods=window)
        .apply(_last_value_percentile, raw=True)
    )
    return result


def detect_peak_trough(
    frame: pd.DataFrame,
    *,
    lookback_window: int,
    value_column: str = "value",
    peak_column: str = "is_local_peak",
    trough_column: str = "is_local_trough",
) -> pd.DataFrame:
    """Detect trailing local peaks and troughs without future observations."""

    _validate_window(lookback_window)
    result = frame.copy()
    rolling = result[value_column].rolling(window=lookback_window, min_periods=lookback_window)
    rolling_max = rolling.max()
    rolling_min = rolling.min()
    current = result[value_column]
    result[peak_column] = (current.notna() & current.eq(rolling_max)).fillna(False)
    result[trough_column] = (current.notna() & current.eq(rolling_min)).fillna(False)
    result.loc[rolling_max.isna(), peak_column] = False
    result.loc[rolling_min.isna(), trough_column] = False
    return result


def _linear_slope(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    x = np.arange(len(values), dtype=float)
    y = values.astype(float)
    x_centered = x - x.mean()
    denominator = float(np.dot(x_centered, x_centered))
    if denominator == 0:
        return np.nan
    return float(np.dot(x_centered, y - y.mean()) / denominator)


def _last_value_percentile(values: np.ndarray) -> float:
    if np.isnan(values).any():
        return np.nan
    current = values[-1]
    less_than = float(np.sum(values < current))
    equal_to = float(np.sum(values == current))
    return (less_than + 0.5 * equal_to) / float(len(values))


def _validate_window(window: int) -> None:
    if window <= 0:
        raise ValueError("window must be positive")

