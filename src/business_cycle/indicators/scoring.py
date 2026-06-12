"""Single-indicator trend-aware scoring methods."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from business_cycle.indicators.transformations import (
    add_moving_average,
    add_pct_change,
    add_rolling_percentile,
    add_rolling_slope,
    clean_observations,
    detect_peak_trough,
)


@dataclass(frozen=True)
class IndicatorScoreResult:
    """Score and confidence for one indicator."""

    indicator_id: str
    score: float
    confidence: float
    as_of: str
    method: str
    reason_zh: str
    details: dict[str, Any]


def level_percentile_score(
    observations: pd.DataFrame,
    *,
    indicator_id: str,
    direction: str,
    window: int | None = None,
    min_periods: int = 12,
    stale_after_days: int | None = None,
    as_of: str | date | None = None,
) -> IndicatorScoreResult:
    """Score the latest level by its trailing historical percentile."""

    cleaned = _prepare_observations(observations, as_of=as_of)
    method = "level_percentile_score"
    if cleaned.empty:
        return _empty_result(indicator_id, method, as_of, "沒有可用資料。")

    latest_date = _latest_date(cleaned)
    values = cleaned["value"]
    valid_count = int(values.notna().sum())
    if valid_count == 0:
        return _result(indicator_id, 50.0, 0.0, latest_date, method, "資料皆為缺值。", {})

    percentile_window = window or len(cleaned)
    scored = add_rolling_percentile(
        cleaned,
        window=percentile_window,
        value_column="value",
        output_column="percentile",
    )
    percentile = _latest_non_nan(scored["percentile"])
    if percentile is None and window is None:
        percentile = _historical_percentile(values.dropna().to_numpy(dtype=float))

    if percentile is None:
        score = 50.0
        reason = "歷史資料不足，無法建立可靠分位數。"
    else:
        score = _score_from_percentile(percentile, direction)
        reason = "以歷史分位數衡量目前水準，並依指標方向轉換為分數。"

    confidence = _base_confidence(valid_count, min_periods)
    confidence *= _missing_penalty(cleaned["value"])
    confidence *= _stale_penalty(latest_date, stale_after_days, as_of)
    if percentile is None:
        confidence *= 0.5

    return _result(
        indicator_id,
        score,
        confidence,
        latest_date,
        method,
        reason,
        {
            "direction": direction,
            "percentile": percentile,
            "window": percentile_window,
            "valid_observations": valid_count,
            "min_periods": min_periods,
        },
    )


def moving_average_slope_score(
    observations: pd.DataFrame,
    *,
    indicator_id: str,
    direction: str,
    moving_average_window: int = 3,
    slope_window: int = 3,
    confirmation_window: int = 3,
    min_periods: int | None = None,
    stale_after_days: int | None = None,
    as_of: str | date | None = None,
) -> IndicatorScoreResult:
    """Score a smoothed trend direction using trailing moving-average slope."""

    cleaned = _prepare_observations(observations, as_of=as_of)
    method = "moving_average_slope_score"
    required = min_periods or moving_average_window + slope_window + confirmation_window - 2
    if cleaned.empty:
        return _empty_result(indicator_id, method, as_of, "沒有可用資料。")

    latest_date = _latest_date(cleaned)
    valid_count = int(cleaned["value"].notna().sum())
    scored = add_moving_average(
        cleaned,
        window=moving_average_window,
        value_column="value",
        output_column="moving_average",
    )
    scored = add_rolling_slope(
        scored,
        window=slope_window,
        value_column="moving_average",
        output_column="slope",
    )
    recent_slopes = scored["slope"].dropna().tail(confirmation_window)
    if recent_slopes.empty:
        signal = 0.0
        score = 50.0
        reason = "資料不足，尚無法確認移動平均斜率。"
    else:
        avg_slope = float(recent_slopes.mean())
        scale = _scale_from_series(scored["moving_average"].dropna().diff())
        signal = float(np.tanh(avg_slope / scale))
        score = _score_from_signed_signal(signal, positive_direction=direction == "rising_is_better")
        reason = "以移動平均斜率與確認窗判斷趨勢方向。"

    confidence = _base_confidence(valid_count, required)
    confidence *= min(1.0, len(recent_slopes) / float(confirmation_window))
    confidence *= _missing_penalty(cleaned["value"])
    confidence *= _stale_penalty(latest_date, stale_after_days, as_of)

    return _result(
        indicator_id,
        score,
        confidence,
        latest_date,
        method,
        reason,
        {
            "direction": direction,
            "moving_average_window": moving_average_window,
            "slope_window": slope_window,
            "confirmation_window": confirmation_window,
            "recent_slopes": recent_slopes.tolist(),
            "signal": signal,
        },
    )


def yoy_momentum_score(
    observations: pd.DataFrame,
    *,
    indicator_id: str,
    direction: str,
    periods: int = 12,
    momentum_window: int = 3,
    min_periods: int | None = None,
    stale_after_days: int | None = None,
    as_of: str | date | None = None,
) -> IndicatorScoreResult:
    """Score year-over-year or period-over-period growth momentum."""

    cleaned = _prepare_observations(observations, as_of=as_of)
    method = "yoy_momentum_score"
    required = min_periods or periods + momentum_window + 1
    if cleaned.empty:
        return _empty_result(indicator_id, method, as_of, "沒有可用資料。")

    latest_date = _latest_date(cleaned)
    valid_count = int(cleaned["value"].notna().sum())
    scored = add_pct_change(
        cleaned,
        periods=periods,
        value_column="value",
        output_column="growth",
    )
    scored["momentum"] = scored["growth"] - scored["growth"].shift(momentum_window)
    latest_growth = _latest_non_nan(scored["growth"])
    latest_momentum = _latest_non_nan(scored["momentum"])
    if latest_growth is None or latest_momentum is None:
        signal = 0.0
        score = 50.0
        reason = "資料不足，尚無法計算成長率與動能變化。"
    else:
        scale = _scale_from_series(scored["growth"].dropna())
        combined = latest_growth + latest_momentum
        signal = float(np.tanh(combined / scale))
        score = _score_from_signed_signal(signal, positive_direction=direction == "higher_is_better")
        reason = "以成長率與成長動能變化衡量單一指標趨勢。"

    confidence = _base_confidence(valid_count, required)
    confidence *= _missing_penalty(cleaned["value"])
    confidence *= _stale_penalty(latest_date, stale_after_days, as_of)
    if latest_growth is None or latest_momentum is None:
        confidence *= 0.5

    return _result(
        indicator_id,
        score,
        confidence,
        latest_date,
        method,
        reason,
        {
            "direction": direction,
            "periods": periods,
            "momentum_window": momentum_window,
            "latest_growth": latest_growth,
            "latest_momentum": latest_momentum,
            "signal": signal,
        },
    )


def peak_trough_reversal_score(
    observations: pd.DataFrame,
    *,
    indicator_id: str,
    mode: str,
    lookback_window: int = 6,
    confirmation_window: int = 3,
    min_periods: int | None = None,
    stale_after_days: int | None = None,
    as_of: str | date | None = None,
) -> IndicatorScoreResult:
    """Score a confirmed trough recovery or peak rollover."""

    cleaned = _prepare_observations(observations, as_of=as_of)
    method = "peak_trough_reversal_score"
    required = min_periods or lookback_window + confirmation_window
    if cleaned.empty:
        return _empty_result(indicator_id, method, as_of, "沒有可用資料。")

    latest_date = _latest_date(cleaned)
    valid_count = int(cleaned["value"].notna().sum())
    detected = detect_peak_trough(
        cleaned,
        lookback_window=lookback_window,
        value_column="value",
    )
    score, confirmed, pivot_index = _confirmed_reversal_score(
        detected,
        mode=mode,
        confirmation_window=confirmation_window,
    )
    reason = (
        "反轉已通過確認窗。"
        if confirmed
        else "尚未通過確認窗，單一 observation 不足以確認反轉。"
    )

    confidence = _base_confidence(valid_count, required)
    confidence *= _missing_penalty(cleaned["value"])
    confidence *= _stale_penalty(latest_date, stale_after_days, as_of)
    if not confirmed:
        confidence *= 0.7

    return _result(
        indicator_id,
        score,
        confidence,
        latest_date,
        method,
        reason,
        {
            "mode": mode,
            "lookback_window": lookback_window,
            "confirmation_window": confirmation_window,
            "confirmed": confirmed,
            "pivot_index": pivot_index,
        },
    )


def _prepare_observations(
    observations: pd.DataFrame,
    *,
    as_of: str | date | None,
) -> pd.DataFrame:
    cleaned = clean_observations(observations)
    if as_of is not None:
        as_of_timestamp = pd.to_datetime(as_of)
        cleaned = cleaned[cleaned["date"] <= as_of_timestamp]
    return cleaned.reset_index(drop=True)


def _confirmed_reversal_score(
    frame: pd.DataFrame,
    *,
    mode: str,
    confirmation_window: int,
) -> tuple[float, bool, int | None]:
    if confirmation_window <= 1 or len(frame) <= confirmation_window:
        return 50.0, False, None

    values = frame["value"]
    if mode == "trough_recovery":
        pivot_candidates = frame.index[frame["is_local_trough"]].tolist()
        direction = 1.0
    elif mode == "peak_rollover":
        pivot_candidates = frame.index[frame["is_local_peak"]].tolist()
        direction = -1.0
    else:
        raise ValueError("mode must be trough_recovery or peak_rollover")

    for pivot_index in reversed(pivot_candidates):
        post_pivot = values.iloc[pivot_index : pivot_index + confirmation_window + 1]
        if len(post_pivot) < confirmation_window + 1 or post_pivot.isna().any():
            continue
        diffs = post_pivot.diff().dropna()
        if (direction * diffs > 0).all() and pivot_index + confirmation_window == len(frame) - 1:
            return 85.0, True, int(pivot_index)

    return 50.0, False, None


def _score_from_percentile(percentile: float, direction: str) -> float:
    if direction == "higher_is_better":
        return _clamp_score(percentile * 100.0)
    if direction == "lower_is_better":
        return _clamp_score((1.0 - percentile) * 100.0)
    if direction == "neutral_midpoint":
        return _clamp_score((1.0 - abs(percentile - 0.5) * 2.0) * 100.0)
    raise ValueError("direction must be higher_is_better, lower_is_better, or neutral_midpoint")


def _score_from_signed_signal(signal: float, *, positive_direction: bool) -> float:
    signed = signal if positive_direction else -signal
    return _clamp_score((signed + 1.0) * 50.0)


def _historical_percentile(values: np.ndarray) -> float | None:
    if len(values) == 0:
        return None
    current = values[-1]
    less_than = float(np.sum(values < current))
    equal_to = float(np.sum(values == current))
    return (less_than + 0.5 * equal_to) / float(len(values))


def _latest_non_nan(series: pd.Series) -> float | None:
    valid = series.dropna()
    if valid.empty:
        return None
    return float(valid.iloc[-1])


def _latest_date(frame: pd.DataFrame) -> str:
    return pd.Timestamp(frame["date"].iloc[-1]).date().isoformat()


def _base_confidence(valid_count: int, min_periods: int) -> float:
    if min_periods <= 0:
        return 1.0
    return _clamp_confidence(valid_count / float(min_periods))


def _missing_penalty(series: pd.Series) -> float:
    if len(series) == 0:
        return 0.0
    missing_share = float(series.isna().mean())
    return _clamp_confidence(1.0 - missing_share)


def _stale_penalty(
    latest_date: str,
    stale_after_days: int | None,
    as_of: str | date | None,
) -> float:
    if stale_after_days is None:
        return 1.0
    reference_date = date.today() if as_of is None else pd.Timestamp(as_of).date()
    age_days = (reference_date - pd.Timestamp(latest_date).date()).days
    return 0.5 if age_days > stale_after_days else 1.0


def _scale_from_series(series: pd.Series) -> float:
    clean = series.dropna()
    if clean.empty:
        return 1.0
    scale = float(clean.std(ddof=0))
    if scale == 0.0 or np.isnan(scale):
        fallback = float(clean.abs().mean())
        return fallback if fallback > 0.0 else 1.0
    return scale


def _empty_result(
    indicator_id: str,
    method: str,
    as_of: str | date | None,
    reason_zh: str,
) -> IndicatorScoreResult:
    as_of_text = date.today().isoformat() if as_of is None else str(as_of)
    return _result(indicator_id, 50.0, 0.0, as_of_text, method, reason_zh, {})


def _result(
    indicator_id: str,
    score: float,
    confidence: float,
    as_of: str,
    method: str,
    reason_zh: str,
    details: dict[str, Any],
) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=_clamp_score(score),
        confidence=_clamp_confidence(confidence),
        as_of=as_of,
        method=method,
        reason_zh=reason_zh,
        details=details,
    )


def _clamp_score(value: float) -> float:
    return float(min(100.0, max(0.0, value)))


def _clamp_confidence(value: float) -> float:
    return float(min(1.0, max(0.0, value)))

