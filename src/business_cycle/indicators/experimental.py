"""Experimental candidate indicator scoring helpers.

These helpers are intentionally separate from live indicator and phase scoring.
Scores represent recession-confirmation signal strength for diagnostics only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from business_cycle.indicators.transformations import clean_observations


@dataclass(frozen=True)
class ExperimentalIndicatorScore:
    """Experimental score for a candidate indicator."""

    indicator_id: str
    score: float | None
    confidence: float
    reason_zh: str
    latest_date: str
    metadata: dict[str, Any]


def sustained_deterioration_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "experimental_indicator",
    direction: str = "higher_is_worse",
    as_of: str | date | None = None,
    moving_average_window: int = 4,
    slope_window: int = 4,
    yoy_periods: int = 52,
    persistence_window: int = 4,
    min_periods: int | None = None,
) -> ExperimentalIndicatorScore:
    """Score sustained deterioration using smoothed trend, YoY change, and persistence."""

    cleaned = _prepare(series, as_of=as_of)
    required = min_periods or max(moving_average_window + slope_window + persistence_window, yoy_periods + 1)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "sustained_deterioration_score"})

    features = _trend_features(
        cleaned,
        moving_average_window=moving_average_window,
        slope_window=slope_window,
        yoy_periods=yoy_periods,
        persistence_window=persistence_window,
    )
    if features["latest_slope"] is None or features["latest_yoy"] is None:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認持續惡化。",
            features,
            required,
            "sustained_deterioration_score",
        )

    signed_slope = _signed(features["latest_slope"], direction)
    signed_yoy = _signed(features["latest_yoy"], direction)
    persistence = _signed_persistence(features["recent_slopes"], direction, persistence_window)
    score = _clamp_score(50.0 + 25.0 * _tanh_signal(signed_slope, features["slope_scale"]) + 25.0 * persistence)
    if signed_yoy > 0:
        score = _clamp_score(score + 10.0 * _tanh_signal(signed_yoy, features["yoy_scale"]))
    confidence = _confidence(cleaned, required) * max(0.35, persistence)
    if persistence < 0.5:
        confidence *= 0.65
    reason = "以移動平均斜率、年變化與持續性檢查是否為連續惡化，而非單期跳動。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "sustained_deterioration_score",
        {**features, "deterioration_share": persistence},
    )


def level_and_trend_confirmation_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "experimental_indicator",
    direction: str = "higher_is_worse",
    as_of: str | date | None = None,
    percentile_window: int = 120,
    moving_average_window: int = 3,
    slope_window: int = 3,
    persistence_window: int = 3,
    min_periods: int = 36,
) -> ExperimentalIndicatorScore:
    """Score elevated level plus trend confirmation."""

    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "level_and_trend_confirmation_score"})

    percentile = _rolling_percentile(cleaned["value"], percentile_window)
    features = _trend_features(
        cleaned,
        moving_average_window=moving_average_window,
        slope_window=slope_window,
        yoy_periods=12,
        persistence_window=persistence_window,
    )
    if percentile is None or features["latest_slope"] is None:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法同時確認水準與趨勢。",
            {**features, "percentile": percentile},
            min_periods,
            "level_and_trend_confirmation_score",
        )

    level_signal = percentile if direction == "higher_is_worse" else 1.0 - percentile
    persistence = _signed_persistence(features["recent_slopes"], direction, persistence_window)
    trend_signal = max(0.0, _tanh_signal(_signed(features["latest_slope"], direction), features["slope_scale"]))
    score = _clamp_score(100.0 * (0.65 * level_signal + 0.35 * trend_signal))
    confidence = _confidence(cleaned, min_periods) * max(0.5, persistence)
    reason = "以歷史分位數與移動平均趨勢共同確認壓力是否偏高且仍在惡化。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "level_and_trend_confirmation_score",
        {**features, "percentile": percentile, "deterioration_share": persistence},
    )


def credit_stress_score(
    spread_series: pd.DataFrame,
    *,
    indicator_id: str = "credit_spread_baa_aaa",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score credit stress from a spread series."""

    return level_and_trend_confirmation_score(
        spread_series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        percentile_window=120,
        moving_average_window=4,
        slope_window=4,
        persistence_window=4,
        min_periods=60,
    )


def financial_stress_confirmation_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "financial_stress_index",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score elevated and persistent financial stress."""

    return level_and_trend_confirmation_score(
        series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        percentile_window=156,
        moving_average_window=4,
        slope_window=4,
        persistence_window=4,
        min_periods=78,
    )


def broad_consumption_deterioration_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "real_personal_consumption_expenditures",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score broad consumption deterioration."""

    return sustained_deterioration_score(
        series,
        indicator_id=indicator_id,
        direction="lower_is_worse",
        as_of=as_of,
        moving_average_window=3,
        slope_window=3,
        yoy_periods=12,
        persistence_window=3,
        min_periods=24,
    )


def production_deterioration_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "industrial_production",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score production deterioration."""

    return sustained_deterioration_score(
        series,
        indicator_id=indicator_id,
        direction="lower_is_worse",
        as_of=as_of,
        moving_average_window=3,
        slope_window=3,
        yoy_periods=12,
        persistence_window=3,
        min_periods=24,
    )


def yield_curve_inversion_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "yield_curve_10y_3m",
    as_of: str | date | None = None,
    moving_average_window: int = 5,
    persistence_window: int = 10,
    min_periods: int = 60,
) -> ExperimentalIndicatorScore:
    """Score sustained yield-curve inversion or flattening pressure."""

    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(
            indicator_id,
            as_of,
            "沒有可用資料。",
            {"method": "yield_curve_inversion_pressure_score"},
        )
    if len(cleaned) < moving_average_window:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認殖利率曲線倒掛是否具有持續性。",
            {"moving_average_window": moving_average_window},
            min_periods,
            "yield_curve_inversion_pressure_score",
        )

    values = cleaned["value"].astype(float)
    moving_average = values.rolling(moving_average_window, min_periods=moving_average_window).mean()
    recent = moving_average.dropna().tail(persistence_window)
    if recent.empty:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認殖利率曲線倒掛是否具有持續性。",
            {"moving_average_window": moving_average_window},
            min_periods,
            "yield_curve_inversion_pressure_score",
        )
    inversion_share = float((recent < 0.0).mean())
    latest_level = float(recent.iloc[-1])
    flattening_pressure = max(0.0, _tanh_signal(-latest_level, _scale(moving_average.dropna())))
    score = _clamp_score(25.0 + 45.0 * inversion_share + 30.0 * flattening_pressure)
    confidence = _confidence(cleaned, min_periods) * max(0.35, inversion_share)
    if inversion_share < 0.5:
        confidence *= 0.65
    reason = "以殖利率曲線倒掛程度與持續性觀察榮景期後段風險，避免單期倒掛被過度解讀。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "yield_curve_inversion_pressure_score",
        {
            "moving_average_window": moving_average_window,
            "persistence_window": persistence_window,
            "latest_level": latest_level,
            "inversion_share": inversion_share,
        },
    )


def restrictive_policy_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "fed_policy_restrictive_pressure",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score sustained policy-rate tightening pressure."""

    return level_and_trend_confirmation_score(
        series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        percentile_window=120,
        moving_average_window=3,
        slope_window=12,
        persistence_window=4,
        min_periods=60,
    )


def credit_spread_widening_score(
    spread_series: pd.DataFrame,
    *,
    indicator_id: str = "credit_spread_baa_10y",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score widening BAA-Treasury credit spread pressure."""

    return level_and_trend_confirmation_score(
        spread_series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        percentile_window=120,
        moving_average_window=4,
        slope_window=4,
        persistence_window=4,
        min_periods=60,
    )


def financial_conditions_tightening_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "financial_conditions_tightening",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score tightening financial conditions."""

    return level_and_trend_confirmation_score(
        series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        percentile_window=156,
        moving_average_window=4,
        slope_window=4,
        persistence_window=4,
        min_periods=78,
    )


def commodity_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "oil_price_pressure",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score persistent oil or commodity pressure."""

    return sustained_deterioration_score(
        series,
        indicator_id=indicator_id,
        direction="higher_is_worse",
        as_of=as_of,
        moving_average_window=4,
        slope_window=4,
        yoy_periods=52,
        persistence_window=4,
        min_periods=80,
    )


def labor_market_late_cycle_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "unemployment_rate_cycle_low_pressure",
    as_of: str | date | None = None,
    percentile_window: int = 120,
    moving_average_window: int = 3,
    slope_window: int = 3,
    persistence_window: int = 3,
    min_periods: int = 60,
) -> ExperimentalIndicatorScore:
    """Score unemployment rate rising from a cycle-low zone."""

    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(
            indicator_id,
            as_of,
            "沒有可用資料。",
            {"method": "labor_market_late_cycle_pressure_score"},
        )
    percentile = _rolling_percentile(cleaned["value"], percentile_window)
    features = _trend_features(
        cleaned,
        moving_average_window=moving_average_window,
        slope_window=slope_window,
        yoy_periods=12,
        persistence_window=persistence_window,
    )
    if percentile is None or features["latest_slope"] is None:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認失業率是否由低檔轉弱。",
            {**features, "percentile": percentile},
            min_periods,
            "labor_market_late_cycle_pressure_score",
        )
    low_level_signal = max(0.0, 1.0 - percentile)
    rising_share = _signed_persistence(features["recent_slopes"], "higher_is_worse", persistence_window)
    rising_signal = max(0.0, _tanh_signal(features["latest_slope"], features["slope_scale"]))
    score = _clamp_score(100.0 * (0.35 * low_level_signal + 0.45 * rising_signal + 0.20 * rising_share))
    if rising_share < 0.5:
        score = min(score, 45.0)
    confidence = _confidence(cleaned, min_periods) * max(0.35, rising_share)
    reason = "以失業率是否處於低檔後轉為上升，觀察就業市場由過熱轉弱的後期循環壓力。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "labor_market_late_cycle_pressure_score",
        {**features, "percentile": percentile, "low_level_signal": low_level_signal, "rising_share": rising_share},
    )


def production_momentum_loss_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "industrial_production_momentum_loss",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score industrial production momentum loss."""

    return sustained_deterioration_score(
        series,
        indicator_id=indicator_id,
        direction="lower_is_worse",
        as_of=as_of,
        moving_average_window=3,
        slope_window=3,
        yoy_periods=12,
        persistence_window=3,
        min_periods=24,
    )


def score_to_dict(score: ExperimentalIndicatorScore) -> dict[str, Any]:
    """Serialize an experimental score."""

    return {
        "indicator_id": score.indicator_id,
        "score": score.score,
        "confidence": score.confidence,
        "reason_zh": score.reason_zh,
        "latest_date": score.latest_date,
        "metadata": score.metadata,
    }


def _prepare(series: pd.DataFrame, *, as_of: str | date | None) -> pd.DataFrame:
    cleaned = clean_observations(series)
    if as_of is not None:
        cleaned = cleaned[cleaned["date"] <= pd.Timestamp(as_of)]
    return cleaned.dropna(subset=["value"]).reset_index(drop=True)


def _trend_features(
    frame: pd.DataFrame,
    *,
    moving_average_window: int,
    slope_window: int,
    yoy_periods: int,
    persistence_window: int,
) -> dict[str, Any]:
    values = frame["value"]
    moving_average = values.rolling(moving_average_window, min_periods=moving_average_window).mean()
    slope = moving_average.diff(slope_window) / float(slope_window)
    yoy = values.pct_change(yoy_periods, fill_method=None).replace([np.inf, -np.inf], np.nan)
    recent_slope = slope.dropna().tail(persistence_window)
    recent_yoy = yoy.dropna().tail(persistence_window)
    latest_slope = _latest(recent_slope)
    latest_yoy = _latest(recent_yoy)
    return {
        "moving_average_window": moving_average_window,
        "slope_window": slope_window,
        "yoy_periods": yoy_periods,
        "persistence_window": persistence_window,
        "latest_slope": latest_slope,
        "latest_yoy": latest_yoy,
        "recent_slopes": recent_slope.tolist(),
        "recent_yoy": recent_yoy.tolist(),
        "deterioration_share": None,
        "slope_scale": _scale(slope.dropna()),
        "yoy_scale": _scale(yoy.dropna()),
    }


def _rolling_percentile(values: pd.Series, window: int) -> float | None:
    clean = values.dropna()
    if clean.empty:
        return None
    sample = clean.tail(window)
    if len(sample) < min(window, 12):
        return None
    current = float(sample.iloc[-1])
    less_than = float(np.sum(sample.to_numpy(dtype=float) < current))
    equal_to = float(np.sum(sample.to_numpy(dtype=float) == current))
    return (less_than + 0.5 * equal_to) / float(len(sample))


def _signed_persistence(values: list[float], direction: str, window: int) -> float:
    if window <= 0:
        return 0.0
    signed_values = [_signed(float(value), direction) for value in values if np.isfinite(float(value))]
    positive = [value for value in signed_values if value > 0]
    return len(positive) / float(window)


def _latest(series: pd.Series) -> float | None:
    clean = series.dropna()
    if clean.empty:
        return None
    return float(clean.iloc[-1])


def _signed(value: float, direction: str) -> float:
    if direction == "higher_is_worse":
        return value
    if direction == "lower_is_worse":
        return -value
    raise ValueError("direction must be higher_is_worse or lower_is_worse")


def _tanh_signal(value: float, scale: float) -> float:
    return float(np.tanh(value / scale))


def _scale(series: pd.Series) -> float:
    clean = series.dropna()
    if clean.empty:
        return 1.0
    scale = float(clean.std(ddof=0))
    if not np.isfinite(scale) or scale == 0.0:
        fallback = float(clean.abs().mean())
        return fallback if fallback > 0 else 1.0
    return scale


def _confidence(frame: pd.DataFrame, required: int) -> float:
    valid_count = int(frame["value"].notna().sum())
    return _clamp_confidence(valid_count / float(required))


def _result(
    indicator_id: str,
    score: float | None,
    confidence: float,
    frame: pd.DataFrame,
    reason_zh: str,
    method: str,
    metadata: dict[str, Any],
) -> ExperimentalIndicatorScore:
    latest_date = pd.Timestamp(frame["date"].iloc[-1]).date().isoformat()
    return ExperimentalIndicatorScore(
        indicator_id=indicator_id,
        score=None if score is None else _clamp_score(score),
        confidence=_clamp_confidence(confidence),
        reason_zh=reason_zh,
        latest_date=latest_date,
        metadata={"method": method, **metadata},
    )


def _empty_result(
    indicator_id: str,
    as_of: str | date | None,
    reason_zh: str,
    metadata: dict[str, Any],
) -> ExperimentalIndicatorScore:
    latest_date = date.today().isoformat() if as_of is None else str(as_of)
    return ExperimentalIndicatorScore(
        indicator_id=indicator_id,
        score=None,
        confidence=0.0,
        reason_zh=reason_zh,
        latest_date=latest_date,
        metadata=metadata,
    )


def _low_information_result(
    indicator_id: str,
    frame: pd.DataFrame,
    reason_zh: str,
    metadata: dict[str, Any],
    required: int,
    method: str,
) -> ExperimentalIndicatorScore:
    return _result(
        indicator_id,
        50.0,
        _confidence(frame, required) * 0.35,
        frame,
        reason_zh,
        method,
        metadata,
    )


def _clamp_score(value: float) -> float:
    return float(min(100.0, max(0.0, value)))


def _clamp_confidence(value: float) -> float:
    return float(min(1.0, max(0.0, value)))
