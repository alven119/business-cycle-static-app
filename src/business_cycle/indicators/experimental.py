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


def yield_curve_lead_time_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "yield_curve_10y_3m",
    as_of: str | date | None = None,
    config: dict[str, Any] | None = None,
) -> ExperimentalIndicatorScore:
    """Score yield-curve lead-time pressure after sustained inversion."""

    cfg = config or {}
    inversion_threshold = float(cfg.get("inversion_threshold", 0.0))
    near_inversion_threshold = float(cfg.get("near_inversion_threshold", 0.25))
    min_share = float(cfg.get("sustained_inversion_min_share", 0.6))
    lookback_months = int(cfg.get("inversion_lookback_months", 18))
    min_sustained_months = int(cfg.get("min_sustained_inversion_months", 3))
    max_lead_time_months = int(cfg.get("max_lead_time_months", 18))
    near_score_floor = float(cfg.get("near_inversion_score_floor", 55.0))
    post_inversion_floor = float(cfg.get("post_inversion_warning_floor", 68.0))
    lead_start, lead_end = cfg.get("peak_warning_months_after_inversion", [3, 18])
    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(
            indicator_id,
            as_of,
            "沒有可用資料。",
            {"method": "yield_curve_lead_time_pressure_score"},
        )

    recent = _since_months(cleaned, lookback_months)
    if len(recent) < 6:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認殖利率曲線倒掛後的 lead-time pressure。",
            {"lookback_months": lookback_months},
            60,
            "yield_curve_lead_time_pressure_score",
        )

    values = recent["value"].astype(float)
    inversion_mask = values < inversion_threshold
    near_inversion_mask = values <= near_inversion_threshold
    inversion_share = float(inversion_mask.mean())
    near_inversion_share = float(near_inversion_mask.mean())
    latest_level = float(values.iloc[-1])
    inversion_dates = recent.loc[inversion_mask, "date"]
    last_inversion_date = None if inversion_dates.empty else pd.Timestamp(inversion_dates.iloc[-1])
    latest_date = pd.Timestamp(cleaned["date"].iloc[-1])
    months_since_last = None if last_inversion_date is None else _month_delta(last_inversion_date, latest_date)
    sustained_run = _first_sustained_true_run(recent, inversion_mask, min_sustained_months)
    near_sustained_run = _first_sustained_true_run(recent, near_inversion_mask, min_sustained_months)
    first_sustained_date = sustained_run[0]
    sustained_detected = bool(sustained_run[0] is not None or inversion_share >= min_share)
    near_sustained_detected = bool(near_sustained_run[0] is not None or near_inversion_share >= min_share)
    months_since_sustained = (
        None if first_sustained_date is None else _month_delta(first_sustained_date, latest_date)
    )
    lead_active = bool(
        sustained_detected
        and months_since_last is not None
        and 0 <= months_since_last <= max_lead_time_months
    )
    post_inversion_values = values.loc[inversion_mask.cumsum() > 0]
    post_inversion_max = float(post_inversion_values.max()) if not post_inversion_values.empty else latest_level
    resteepening = bool(inversion_share > 0 and latest_level > inversion_threshold and post_inversion_max > inversion_threshold)
    inversion_pressure = min(1.0, inversion_share / max(min_share, 0.01))
    near_pressure = min(1.0, near_inversion_share / max(min_share, 0.01))
    persistence_pressure = max(
        inversion_pressure,
        near_pressure * 0.75,
        min(1.0, sustained_run[1] / max(min_sustained_months, 1)),
    )
    current_curve_component = _yield_curve_current_component(
        latest_level=latest_level,
        inversion_threshold=inversion_threshold,
        near_inversion_threshold=near_inversion_threshold,
        near_score_floor=near_score_floor,
        values=values,
    )
    persistence_component = 100.0 * persistence_pressure
    lead_time_component = 0.0
    if lead_active:
        lead_time_component = post_inversion_floor
        if months_since_last is not None and int(lead_start) <= months_since_last <= int(lead_end):
            lead_time_component = max(lead_time_component, 75.0)
        if latest_level < inversion_threshold:
            lead_time_component = max(lead_time_component, 82.0)
        if resteepening:
            lead_time_component = min(100.0, lead_time_component + 8.0)
    elif near_sustained_detected:
        lead_time_component = near_score_floor

    final_score_before_confidence = max(
        current_curve_component,
        lead_time_component,
        0.45 * lead_time_component + 0.35 * persistence_component + 0.20 * current_curve_component,
    )
    score = _clamp_score(final_score_before_confidence)
    confidence = _confidence(cleaned, 60) * min(1.0, 0.35 + 0.45 * persistence_pressure + (0.20 if lead_active else 0.0))
    confidence_reason = "sustained_inversion_detected" if sustained_detected else "near_inversion_or_limited_persistence"
    if not sustained_detected and not near_sustained_detected:
        confidence *= 0.65
        confidence_reason = "single_or_sparse_inversion"
    if months_since_last is not None and months_since_last > max_lead_time_months and latest_level > near_inversion_threshold:
        confidence *= 0.8
        confidence_reason = "outside_lead_time_window"
    reason = "以持續倒掛後的 6～18 個月 lead-time window 評估榮景期結束風險，而非只看當期倒掛。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "yield_curve_lead_time_pressure_score",
        {
            "latest_level": latest_level,
            "inversion_share": inversion_share,
            "sustained_inversion_detected": sustained_detected,
            "first_sustained_inversion_date": _date_or_none(first_sustained_date),
            "last_inversion_date": _date_or_none(last_inversion_date),
            "months_since_last_inversion": months_since_last,
            "months_since_sustained_inversion": months_since_sustained,
            "lead_time_window_active": lead_active,
            "resteepening_after_inversion": resteepening,
            "current_curve_component": current_curve_component,
            "lead_time_component": lead_time_component,
            "persistence_component": persistence_component,
            "final_score_before_confidence": final_score_before_confidence,
            "confidence_reason": confidence_reason,
            "lookback_months": lookback_months,
        },
    )


def credit_spread_velocity_score(
    primary_spread_series: pd.DataFrame,
    alternative_spread_series: pd.DataFrame | None = None,
    *,
    indicator_id: str = "credit_spread_baa_10y",
    as_of: str | date | None = None,
    config: dict[str, Any] | None = None,
) -> ExperimentalIndicatorScore:
    """Score credit spread pressure from percentile and widening velocity."""

    cfg = config or {}
    velocity_window = int(cfg.get("velocity_window_months", 6))
    percentile_window = int(cfg.get("percentile_window_years", 10)) * 12
    widening_min_share = float(cfg.get("widening_min_share", 0.5))
    primary = _credit_spread_candidate(
        primary_spread_series,
        as_of=as_of,
        name="BAA - DGS10",
        velocity_window=velocity_window,
        percentile_window=percentile_window,
    )
    candidates = [primary]
    if alternative_spread_series is not None:
        candidates.append(
            _credit_spread_candidate(
                alternative_spread_series,
                as_of=as_of,
                name="BAA - AAA",
                velocity_window=velocity_window,
                percentile_window=percentile_window,
            )
        )
    best = max(candidates, key=lambda item: item["score"])
    frame = best["frame"]
    if frame.empty:
        return _empty_result(
            indicator_id,
            as_of,
            "沒有可用資料。",
            {"method": "credit_spread_velocity_score"},
        )
    if best["percentile"] is None or best["velocity"] is None:
        return _low_information_result(
            indicator_id,
            frame,
            "資料不足，尚無法確認信用利差分位數與擴大速度。",
            best,
            60,
            "credit_spread_velocity_score",
        )
    widening_share = float(best["widening_share"])
    velocity_signal = max(0.0, _tanh_signal(float(best["velocity"]), best["velocity_scale"]))
    score = _clamp_score(100.0 * (0.45 * float(best["percentile"]) + 0.35 * velocity_signal + 0.20 * min(1.0, widening_share / max(widening_min_share, 0.01))))
    confidence = _confidence(frame, 60) * max(0.45, widening_share)
    reason = "以信用利差分位數與擴大速度比較 credit stress proxy，降低單一利率水準造成的失真。"
    return _result(
        indicator_id,
        score,
        confidence,
        frame,
        reason,
        "credit_spread_velocity_score",
        {
            "selected_spread": best["name"],
            "latest_spread": best["latest_spread"],
            "spread_percentile": best["percentile"],
            "spread_velocity": best["velocity"],
            "widening_share": widening_share,
            "alternative_spreads_checked": [item["name"] for item in candidates],
        },
    )


def financial_conditions_delta_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "financial_conditions_tightening",
    as_of: str | date | None = None,
    config: dict[str, Any] | None = None,
) -> ExperimentalIndicatorScore:
    """Score financial conditions using level percentile and deterioration velocity."""

    cfg = config or {}
    delta_window = int(cfg.get("delta_window_months", 6))
    percentile_window = int(cfg.get("level_percentile_window_years", 10)) * 12
    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "financial_conditions_delta_score"})
    percentile = _rolling_percentile(cleaned["value"], percentile_window)
    delta_series = cleaned["value"].astype(float).diff(delta_window)
    delta = _latest(delta_series)
    delta_percentile = _rolling_percentile(delta_series.dropna().reset_index(drop=True), percentile_window)
    if percentile is None or delta is None:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認金融條件水準與惡化速度。",
            {"level_percentile": percentile, "delta": delta},
            60,
            "financial_conditions_delta_score",
        )
    delta_signal = max(0.0, _tanh_signal(delta, _scale(delta_series.dropna())))
    score = _clamp_score(100.0 * (0.50 * percentile + 0.35 * delta_signal + 0.15 * (delta_percentile or 0.0)))
    confidence = _confidence(cleaned, 60)
    reason = "以金融條件水準分位數與近期惡化速度評估 late-cycle tightening pressure。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "financial_conditions_delta_score",
        {
            "latest_level": float(cleaned["value"].iloc[-1]),
            "level_percentile": percentile,
            "delta": delta,
            "delta_percentile": delta_percentile,
        },
    )


def fed_policy_peak_pause_pressure_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "fed_policy_restrictive_pressure",
    as_of: str | date | None = None,
    config: dict[str, Any] | None = None,
) -> ExperimentalIndicatorScore:
    """Score policy pressure from high rates, recent hikes, and peak/pause behavior."""

    cfg = config or {}
    high_level_percentile = float(cfg.get("high_level_percentile", 0.75))
    recent_hike_window = int(cfg.get("recent_hike_window_months", 18))
    pause_window = int(cfg.get("peak_or_pause_window_months", 6))
    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "fed_policy_peak_pause_pressure_score"})
    percentile = _rolling_percentile(cleaned["value"], 120)
    recent = _since_months(cleaned, recent_hike_window)
    pause_recent = _since_months(cleaned, pause_window)
    if percentile is None or len(recent) < 2:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認政策利率高檔與 peak/pause 壓力。",
            {"rate_percentile": percentile},
            60,
            "fed_policy_peak_pause_pressure_score",
        )
    recent_hike_amount = float(recent["value"].iloc[-1] - recent["value"].iloc[0])
    diffs = cleaned["value"].astype(float).diff()
    hike_dates = cleaned.loc[diffs > 0.01, "date"]
    months_since_last_hike = None if hike_dates.empty else _month_delta(pd.Timestamp(hike_dates.iloc[-1]), pd.Timestamp(cleaned["date"].iloc[-1]))
    pause_delta = float(pause_recent["value"].iloc[-1] - pause_recent["value"].iloc[0]) if len(pause_recent) >= 2 else 0.0
    high_level_signal = 1.0 if percentile >= high_level_percentile else percentile / max(high_level_percentile, 0.01)
    hike_signal = max(0.0, _tanh_signal(recent_hike_amount, _scale(recent["value"].diff().dropna())))
    pause_signal = 1.0 if recent_hike_amount > 0 and abs(pause_delta) <= 0.1 else 0.0
    score = _clamp_score(100.0 * (0.45 * high_level_signal + 0.35 * hike_signal + 0.20 * pause_signal))
    confidence = _confidence(cleaned, 60)
    reason = "以政策利率高檔、近期升息與升息後停留高檔觀察 late-cycle policy pressure。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "fed_policy_peak_pause_pressure_score",
        {
            "rate_percentile": percentile,
            "recent_hike_amount": recent_hike_amount,
            "months_since_last_hike": months_since_last_hike,
            "pause_delta": pause_delta,
        },
    )


def peak_reversal_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "initial_jobless_claims_peak_reversal",
    direction: str = "down_from_peak",
    as_of: str | date | None = None,
    moving_average_window: int = 4,
    peak_lookback_periods: int = 26,
    persistence_window: int = 4,
    min_periods: int = 30,
) -> ExperimentalIndicatorScore:
    """Score sustained reversal down from a recent peak."""

    if direction != "down_from_peak":
        raise ValueError("direction must be down_from_peak")
    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "peak_reversal_score"})
    smoothed = cleaned["value"].astype(float).rolling(
        moving_average_window,
        min_periods=moving_average_window,
    ).mean()
    recent = smoothed.dropna().tail(peak_lookback_periods)
    if len(recent) < max(persistence_window + 1, 8):
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認是否已從高點持續回落。",
            {"moving_average_window": moving_average_window, "peak_lookback_periods": peak_lookback_periods},
            min_periods,
            "peak_reversal_score",
        )
    recent_peak = float(recent.max())
    latest_value = float(recent.iloc[-1])
    drawdown = 0.0 if recent_peak == 0 else max(0.0, (recent_peak - latest_value) / abs(recent_peak))
    recent_changes = recent.diff().dropna().tail(persistence_window)
    easing_share = float((recent_changes < 0.0).mean()) if not recent_changes.empty else 0.0
    slope = float(recent_changes.mean()) if not recent_changes.empty else 0.0
    drawdown_signal = min(1.0, drawdown / 0.20)
    persistence_signal = easing_share
    score = _clamp_score(35.0 + 40.0 * drawdown_signal + 25.0 * persistence_signal)
    if easing_share < 0.5:
        score = min(score, 62.0)
    confidence = _confidence(cleaned, min_periods) * max(0.35, easing_share)
    if easing_share < 0.5:
        confidence *= 0.65
    reason = "以近期高點後的回落幅度與連續性檢查是否出現衰退落底訊號，而非單期跳動。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "peak_reversal_score",
        {
            "recent_peak": recent_peak,
            "latest_value": latest_value,
            "drawdown_from_peak": drawdown,
            "persistence_share": easing_share,
            "recent_slope": slope,
            "moving_average_window": moving_average_window,
            "peak_lookback_periods": peak_lookback_periods,
        },
    )


def bottoming_momentum_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "real_retail_sales_bottoming",
    direction: str = "up_from_trough",
    as_of: str | date | None = None,
    moving_average_window: int = 3,
    trough_lookback_periods: int = 18,
    persistence_window: int = 3,
    min_periods: int = 24,
) -> ExperimentalIndicatorScore:
    """Score sustained rebound up from a recent trough."""

    if direction != "up_from_trough":
        raise ValueError("direction must be up_from_trough")
    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "bottoming_momentum_score"})
    smoothed = cleaned["value"].astype(float).rolling(
        moving_average_window,
        min_periods=moving_average_window,
    ).mean()
    recent = smoothed.dropna().tail(trough_lookback_periods)
    if len(recent) < max(persistence_window + 1, 8):
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認是否已由低點持續回升。",
            {"moving_average_window": moving_average_window, "trough_lookback_periods": trough_lookback_periods},
            min_periods,
            "bottoming_momentum_score",
        )
    recent_trough = float(recent.min())
    latest_value = float(recent.iloc[-1])
    rebound = 0.0 if recent_trough == 0 else max(0.0, (latest_value - recent_trough) / abs(recent_trough))
    recent_slopes = recent.diff().dropna().tail(persistence_window)
    rebound_share = float((recent_slopes > 0.0).mean()) if not recent_slopes.empty else 0.0
    slope_signal = max(0.0, _tanh_signal(float(recent_slopes.mean()), _scale(recent.diff().dropna()))) if not recent_slopes.empty else 0.0
    rebound_signal = min(1.0, rebound / 0.08)
    score = _clamp_score(35.0 + 35.0 * rebound_signal + 20.0 * rebound_share + 10.0 * slope_signal)
    if rebound_share < 0.5:
        score = min(score, 62.0)
    confidence = _confidence(cleaned, min_periods) * max(0.35, rebound_share)
    if rebound_share < 0.5:
        confidence *= 0.65
    reason = "以近期低點後的回升幅度、移動平均斜率與持續性檢查是否有落底回升。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "bottoming_momentum_score",
        {
            "recent_trough": recent_trough,
            "latest_value": latest_value,
            "rebound_from_trough": rebound,
            "persistence_share": rebound_share,
            "recent_slopes": recent_slopes.tolist(),
            "moving_average_window": moving_average_window,
            "trough_lookback_periods": trough_lookback_periods,
        },
    )


def credit_stress_easing_score(
    spread_series: pd.DataFrame,
    *,
    indicator_id: str = "credit_spread_easing",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score easing credit stress from a spread series."""

    score = peak_reversal_score(
        spread_series,
        indicator_id=indicator_id,
        as_of=as_of,
        moving_average_window=3,
        peak_lookback_periods=18,
        persistence_window=3,
        min_periods=36,
    )
    frame = _prepare(spread_series, as_of=as_of)
    if frame.empty:
        return score
    return _result(
        indicator_id,
        score.score,
        score.confidence,
        frame,
        "以信用利差是否自近期高點收斂評估壓力緩解；這不代表信用壓力已消失。",
        "credit_stress_easing_score",
        {
            "recent_peak_spread": score.metadata.get("recent_peak"),
            "latest_spread": score.metadata.get("latest_value"),
            "spread_drawdown": score.metadata.get("drawdown_from_peak"),
            "easing_share": score.metadata.get("persistence_share"),
        },
    )


def financial_stress_easing_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "financial_stress_easing",
    as_of: str | date | None = None,
) -> ExperimentalIndicatorScore:
    """Score financial stress easing from a recent peak."""

    score = peak_reversal_score(
        series,
        indicator_id=indicator_id,
        as_of=as_of,
        moving_average_window=4,
        peak_lookback_periods=26,
        persistence_window=4,
        min_periods=52,
    )
    frame = _prepare(series, as_of=as_of)
    if frame.empty:
        return score
    return _result(
        indicator_id,
        score.score,
        score.confidence,
        frame,
        "以金融壓力是否自近期高點下降評估壓力緩解。",
        "financial_stress_easing_score",
        {
            "recent_peak": score.metadata.get("recent_peak"),
            "latest_level": score.metadata.get("latest_value"),
            "drawdown_from_peak": score.metadata.get("drawdown_from_peak"),
            "easing_share": score.metadata.get("persistence_share"),
        },
    )


def policy_easing_support_score(
    series: pd.DataFrame,
    *,
    indicator_id: str = "fed_policy_easing_signal",
    as_of: str | date | None = None,
    min_periods: int = 36,
) -> ExperimentalIndicatorScore:
    """Score Fed policy easing as recovery support, not standalone confirmation."""

    cleaned = _prepare(series, as_of=as_of)
    if cleaned.empty:
        return _empty_result(indicator_id, as_of, "沒有可用資料。", {"method": "policy_easing_support_score"})
    values = cleaned["value"].astype(float)
    if len(values) < 7:
        return _low_information_result(
            indicator_id,
            cleaned,
            "資料不足，尚無法確認政策是否進入寬鬆。",
            {"required_recent_periods": 7},
            min_periods,
            "policy_easing_support_score",
        )
    rate_change_3m = float(values.iloc[-1] - values.iloc[-4])
    rate_change_6m = float(values.iloc[-1] - values.iloc[-7])
    recent_changes = values.diff().dropna().tail(6)
    easing_share = float((recent_changes < -0.01).mean()) if not recent_changes.empty else 0.0
    easing_magnitude = max(0.0, -rate_change_6m)
    score = _clamp_score(35.0 + 35.0 * min(1.0, easing_magnitude / 2.0) + 30.0 * easing_share)
    if easing_share < 0.34:
        score = min(score, 62.0)
    confidence = _confidence(cleaned, min_periods) * max(0.35, easing_share)
    reason = "以降息幅度與寬鬆持續性判斷政策是否支持復甦；此訊號不能單獨確認復甦。"
    return _result(
        indicator_id,
        score,
        confidence,
        cleaned,
        reason,
        "policy_easing_support_score",
        {
            "rate_change_3m": rate_change_3m,
            "rate_change_6m": rate_change_6m,
            "easing_persistence": easing_share,
            "standalone_recovery_confirmation": False,
        },
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


def _credit_spread_candidate(
    series: pd.DataFrame,
    *,
    as_of: str | date | None,
    name: str,
    velocity_window: int,
    percentile_window: int,
) -> dict[str, Any]:
    frame = _prepare(series, as_of=as_of)
    if frame.empty:
        return {
            "name": name,
            "frame": frame,
            "score": 0.0,
            "percentile": None,
            "velocity": None,
            "latest_spread": None,
            "widening_share": 0.0,
            "velocity_scale": 1.0,
        }
    values = frame["value"].astype(float)
    percentile = _rolling_percentile(values, percentile_window)
    velocity_series = values.diff(velocity_window)
    velocity = _latest(velocity_series)
    recent_changes = values.diff().dropna().tail(velocity_window)
    widening_share = float((recent_changes > 0.0).mean()) if not recent_changes.empty else 0.0
    velocity_scale = _scale(velocity_series.dropna())
    score = 0.0
    if percentile is not None and velocity is not None:
        score = 100.0 * (
            0.45 * percentile
            + 0.35 * max(0.0, _tanh_signal(velocity, velocity_scale))
            + 0.20 * widening_share
        )
    return {
        "name": name,
        "frame": frame,
        "score": score,
        "percentile": percentile,
        "velocity": velocity,
        "latest_spread": float(values.iloc[-1]),
        "widening_share": widening_share,
        "velocity_scale": velocity_scale,
    }


def _first_sustained_true_run(
    frame: pd.DataFrame,
    mask: pd.Series,
    min_months: int,
) -> tuple[pd.Timestamp | None, int]:
    run_start: pd.Timestamp | None = None
    run_length = 0
    max_run_length = 0
    first_sustained: pd.Timestamp | None = None
    for is_true, observed_at in zip(mask.astype(bool), frame["date"], strict=False):
        if is_true:
            if run_length == 0:
                run_start = pd.Timestamp(observed_at)
            run_length += 1
            max_run_length = max(max_run_length, run_length)
            if run_length >= min_months and first_sustained is None:
                first_sustained = run_start
        else:
            run_start = None
            run_length = 0
    return first_sustained, max_run_length


def _yield_curve_current_component(
    *,
    latest_level: float,
    inversion_threshold: float,
    near_inversion_threshold: float,
    near_score_floor: float,
    values: pd.Series,
) -> float:
    scale = _scale(values)
    if latest_level < inversion_threshold:
        return _clamp_score(82.0 + 18.0 * max(0.0, _tanh_signal(-latest_level, scale)))
    if latest_level <= near_inversion_threshold:
        distance = (near_inversion_threshold - latest_level) / max(
            near_inversion_threshold - inversion_threshold,
            0.01,
        )
        return _clamp_score(near_score_floor + 20.0 * max(0.0, min(1.0, distance)))
    steepness_penalty = max(0.0, _tanh_signal(latest_level - near_inversion_threshold, scale))
    return _clamp_score(45.0 - 25.0 * steepness_penalty)


def _date_or_none(value: pd.Timestamp | None) -> str | None:
    if value is None:
        return None
    return value.date().isoformat()


def _since_months(frame: pd.DataFrame, months: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    latest = pd.Timestamp(frame["date"].iloc[-1])
    cutoff = latest - pd.DateOffset(months=months)
    return frame[frame["date"] >= cutoff].reset_index(drop=True)


def _month_delta(start: pd.Timestamp, end: pd.Timestamp) -> int:
    return max(0, (end.year - start.year) * 12 + (end.month - start.month))


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
