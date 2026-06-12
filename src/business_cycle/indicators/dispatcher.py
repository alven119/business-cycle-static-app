"""Dispatch indicator observations to the configured scoring method."""

from __future__ import annotations

from datetime import date
from typing import Any, Callable

import pandas as pd

from business_cycle.indicators.scoring import (
    IndicatorScoreResult,
    level_percentile_score,
    moving_average_slope_score,
    peak_trough_reversal_score,
    yoy_momentum_score,
)
from business_cycle.indicators.specs import IndicatorScoringSpec


class IndicatorScoringError(ValueError):
    """Raised when an indicator scoring spec cannot be dispatched."""


ScoringFunction = Callable[..., IndicatorScoreResult]

SUPPORTED_METHODS: dict[str, ScoringFunction] = {
    "level_percentile_score": level_percentile_score,
    "moving_average_slope_score": moving_average_slope_score,
    "yoy_momentum_score": yoy_momentum_score,
    "peak_trough_reversal_score": peak_trough_reversal_score,
}

REQUIRED_PARAMETERS: dict[str, tuple[str, ...]] = {
    "level_percentile_score": (),
    "moving_average_slope_score": (),
    "yoy_momentum_score": ("periods",),
    "peak_trough_reversal_score": ("mode", "confirmation_window"),
}


def score_indicator(
    observations: pd.DataFrame,
    spec: IndicatorScoringSpec,
    as_of: str | date | None = None,
) -> IndicatorScoreResult:
    """Score one indicator according to its scoring spec."""

    scoring_function = SUPPORTED_METHODS.get(spec.score_method)
    if scoring_function is None:
        supported = ", ".join(sorted(SUPPORTED_METHODS))
        raise IndicatorScoringError(
            f"Unsupported score_method {spec.score_method!r}; supported methods: {supported}"
        )

    _validate_required_parameters(spec)
    normalized = _normalize_observations(observations, spec)
    parameters = dict(spec.parameters)
    direction = _direction_for_method(spec.score_method, spec.direction)

    kwargs: dict[str, Any] = {
        "indicator_id": spec.indicator_id,
        "stale_after_days": spec.stale_after_days,
        "as_of": as_of,
        **parameters,
    }
    if spec.score_method != "peak_trough_reversal_score":
        kwargs["direction"] = direction

    result = scoring_function(normalized, **kwargs)
    return _with_dispatch_details(
        result,
        spec=spec,
        parameters=parameters,
        as_of=as_of,
        available_observations=_available_observations(normalized, as_of=as_of),
    )


def _validate_required_parameters(spec: IndicatorScoringSpec) -> None:
    missing = [
        parameter
        for parameter in REQUIRED_PARAMETERS[spec.score_method]
        if parameter not in spec.parameters
    ]
    if missing:
        missing_text = ", ".join(missing)
        raise IndicatorScoringError(
            f"Indicator {spec.indicator_id!r} score_method {spec.score_method!r} "
            f"is missing required parameter(s): {missing_text}"
        )


def _normalize_observations(
    observations: pd.DataFrame,
    spec: IndicatorScoringSpec,
) -> pd.DataFrame:
    missing_columns = [
        column
        for column in (spec.date_column, spec.value_column)
        if column not in observations.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise IndicatorScoringError(
            f"Indicator {spec.indicator_id!r} observations missing column(s): {missing_text}"
        )

    return observations.rename(
        columns={
            spec.date_column: "date",
            spec.value_column: "value",
        }
    )


def _direction_for_method(method: str, direction: str) -> str:
    if method == "moving_average_slope_score":
        mapping = {
            "higher_is_better": "rising_is_better",
            "higher_is_stronger": "rising_is_better",
            "lower_is_better": "falling_is_better",
            "lower_is_stronger": "falling_is_better",
            "rising_is_better": "rising_is_better",
            "falling_is_better": "falling_is_better",
        }
    elif method in {"level_percentile_score", "yoy_momentum_score"}:
        mapping = {
            "higher_is_better": "higher_is_better",
            "higher_is_stronger": "higher_is_better",
            "lower_is_better": "lower_is_better",
            "lower_is_stronger": "lower_is_better",
            "neutral_midpoint": "neutral_midpoint",
        }
    else:
        return direction

    try:
        return mapping[direction]
    except KeyError as exc:
        allowed = ", ".join(sorted(mapping))
        raise IndicatorScoringError(
            f"Direction {direction!r} is not valid for {method}; allowed: {allowed}"
        ) from exc


def _available_observations(
    observations: pd.DataFrame,
    *,
    as_of: str | date | None,
) -> int:
    frame = observations
    if as_of is not None:
        as_of_timestamp = pd.to_datetime(as_of)
        frame = frame[pd.to_datetime(frame["date"], errors="coerce") <= as_of_timestamp]
    return int(pd.to_numeric(frame["value"], errors="coerce").notna().sum())


def _with_dispatch_details(
    result: IndicatorScoreResult,
    *,
    spec: IndicatorScoringSpec,
    parameters: dict[str, Any],
    as_of: str | date | None,
    available_observations: int,
) -> IndicatorScoreResult:
    details = {
        **result.details,
        "dispatcher": {
            "method": spec.score_method,
            "parameters": parameters,
            "as_of": None if as_of is None else str(as_of),
            "available_observations": available_observations,
            "stale_after_days": spec.stale_after_days,
        },
    }
    return IndicatorScoreResult(
        indicator_id=result.indicator_id,
        score=result.score,
        confidence=result.confidence,
        as_of=result.as_of,
        method=result.method,
        reason_zh=result.reason_zh,
        details=details,
    )

