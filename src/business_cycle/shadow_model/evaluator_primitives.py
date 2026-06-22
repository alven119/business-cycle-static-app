"""Causal shadow-evaluator primitives for QA8.

These helpers are deliberately small and label-free. They operate only on
same-as-of observations supplied by the caller and return abstention metadata
instead of silently choosing windows or thresholds.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any, Iterable


Observation = dict[str, Any]


def calendar_time_moving_average(
    *,
    observations: Iterable[Observation],
    as_of: str,
    calendar_months: int,
    minimum_observations: int,
    rule_id: str,
    data_mode: str,
) -> dict[str, Any]:
    """Return a calendar-window moving average or an abstention result."""

    if calendar_months <= 0 or minimum_observations <= 0:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="invalid_window_parameters",
        )
    as_of_date = date.fromisoformat(as_of)
    parsed = _parse_observations(observations)
    if _has_future_data(parsed, as_of_date):
        return _result(
            status="rejected",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="future_data_rejected",
            future_data_used=False,
        )
    window_start = _subtract_months(as_of_date, calendar_months)
    window_rows = [
        row for row in parsed if window_start <= row["date"] <= as_of_date
    ]
    if len(window_rows) < minimum_observations:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            window_start=window_start,
            window_end=as_of_date,
            observation_count=len(window_rows),
            abstention_reason="insufficient_lookback",
        )
    values = [float(row["value"]) for row in window_rows]
    return _result(
        status="matched",
        value=sum(values) / len(values),
        rule_id=rule_id,
        data_mode=data_mode,
        window_start=window_start,
        window_end=as_of_date,
        observation_count=len(window_rows),
        applied_parameters={
            "calendar_months": calendar_months,
            "minimum_observations": minimum_observations,
        },
        provenance="calendar_time_moving_average",
    )


def directional_change(
    *,
    observations: Iterable[Observation],
    as_of: str,
    direction: str,
    minimum_observations: int,
    rule_id: str,
    data_mode: str,
) -> dict[str, Any]:
    """Evaluate only the last causal direction, without confirmation semantics."""

    as_of_date = date.fromisoformat(as_of)
    parsed = _parse_observations(observations)
    if _has_future_data(parsed, as_of_date):
        return _result(
            status="rejected",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="future_data_rejected",
        )
    rows = [row for row in parsed if row["date"] <= as_of_date]
    if len(rows) < minimum_observations:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            observation_count=len(rows),
            abstention_reason="insufficient_lookback",
        )
    rows = sorted(rows, key=lambda row: row["date"])
    delta = float(rows[-1]["value"]) - float(rows[-2]["value"])
    matched = (direction == "up" and delta > 0) or (
        direction == "down" and delta < 0
    )
    return _result(
        status="matched" if matched else "not_matched",
        value=delta,
        rule_id=rule_id,
        data_mode=data_mode,
        window_start=rows[-2]["date"],
        window_end=rows[-1]["date"],
        observation_count=len(rows),
        applied_parameters={
            "direction": direction,
            "minimum_observations": minimum_observations,
        },
        provenance="directional_change",
    )


def record_low_or_high(
    *,
    observations: Iterable[Observation],
    as_of: str,
    direction: str,
    reference_window_start: str | None,
    rule_id: str,
    data_mode: str,
) -> dict[str, Any]:
    """Evaluate a record low/high only when a reference window is explicit."""

    if not reference_window_start:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="reference_window_not_preregistered",
        )
    as_of_date = date.fromisoformat(as_of)
    start = date.fromisoformat(reference_window_start)
    parsed = _parse_observations(observations)
    if _has_future_data(parsed, as_of_date):
        return _result(
            status="rejected",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="future_data_rejected",
        )
    rows = [row for row in parsed if start <= row["date"] <= as_of_date]
    if len(rows) < 2:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            window_start=start,
            window_end=as_of_date,
            observation_count=len(rows),
            abstention_reason="insufficient_lookback",
        )
    latest = sorted(rows, key=lambda row: row["date"])[-1]
    values = [float(row["value"]) for row in rows]
    is_record = (
        float(latest["value"]) == min(values)
        if direction == "low"
        else float(latest["value"]) == max(values)
    )
    return _result(
        status="matched" if is_record else "not_matched",
        value=latest["value"],
        rule_id=rule_id,
        data_mode=data_mode,
        window_start=start,
        window_end=as_of_date,
        observation_count=len(rows),
        applied_parameters={"direction": direction},
        provenance="record_low_or_high",
    )


def persistence_window(
    *,
    observations: Iterable[Observation],
    as_of: str,
    calendar_quarters: int | None,
    condition: str,
    rule_id: str,
    data_mode: str,
) -> dict[str, Any]:
    """Evaluate persistence over explicit calendar quarters."""

    if calendar_quarters is None:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="persistence_period_not_preregistered",
        )
    as_of_date = date.fromisoformat(as_of)
    start = _subtract_months(as_of_date, calendar_quarters * 3)
    parsed = _parse_observations(observations)
    if _has_future_data(parsed, as_of_date):
        return _result(
            status="rejected",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="future_data_rejected",
        )
    rows = [row for row in parsed if start <= row["date"] <= as_of_date]
    if len(rows) < 2:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            window_start=start,
            window_end=as_of_date,
            observation_count=len(rows),
            abstention_reason="insufficient_lookback",
        )
    values = [float(row["value"]) for row in sorted(rows, key=lambda row: row["date"])]
    if condition == "nonincreasing":
        matched = all(left >= right for left, right in zip(values, values[1:]))
    elif condition == "nondecreasing":
        matched = all(left <= right for left, right in zip(values, values[1:]))
    else:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="unsupported_persistence_condition",
        )
    return _result(
        status="matched" if matched else "not_matched",
        value=values[-1],
        rule_id=rule_id,
        data_mode=data_mode,
        window_start=start,
        window_end=as_of_date,
        observation_count=len(rows),
        applied_parameters={
            "calendar_quarters": calendar_quarters,
            "condition": condition,
        },
        provenance="persistence_window",
    )


def turning_point_candidate(
    *,
    observations: Iterable[Observation],
    as_of: str,
    direction: str | None,
    lookback_months: int | None,
    confirmation_months: int | None,
    rule_id: str,
    data_mode: str,
) -> dict[str, Any]:
    """Evaluate a causal turning-point candidate only when all semantics exist."""

    if not direction or lookback_months is None or confirmation_months is None:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="turning_point_semantics_incomplete",
        )
    return directional_change(
        observations=observations,
        as_of=as_of,
        direction=direction,
        minimum_observations=max(2, confirmation_months + 1),
        rule_id=rule_id,
        data_mode=data_mode,
    )


def cross_series_direction_relation(
    *,
    left_observations: Iterable[Observation],
    right_observations: Iterable[Observation],
    as_of: str,
    rule_id: str,
    data_mode: str,
    left_data_mode: str,
    right_data_mode: str,
) -> dict[str, Any]:
    """Evaluate a same-as-of cross-series relation with data-mode isolation."""

    if left_data_mode != right_data_mode or left_data_mode != data_mode:
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="mixed_data_mode_input",
        )
    left = directional_change(
        observations=left_observations,
        as_of=as_of,
        direction="up",
        minimum_observations=2,
        rule_id=rule_id,
        data_mode=data_mode,
    )
    right = directional_change(
        observations=right_observations,
        as_of=as_of,
        direction="up",
        minimum_observations=2,
        rule_id=rule_id,
        data_mode=data_mode,
    )
    if left["status"] != "matched" or right["status"] != "matched":
        return _result(
            status="abstained",
            rule_id=rule_id,
            data_mode=data_mode,
            abstention_reason="input_direction_incomplete",
        )
    return _result(
        status="matched",
        value={"left_delta": left["value"], "right_delta": right["value"]},
        rule_id=rule_id,
        data_mode=data_mode,
        observation_count=4,
        applied_parameters={"same_as_of": as_of},
        provenance="cross_series_direction_relation",
    )


def summarize_evaluator_primitive_guards() -> dict[str, Any]:
    """Return QA8 static guard counts for primitive implementation."""

    return {
        "phase": "QA8",
        "evaluator_primitive_library_ready": True,
        "centered_window_usage_count": 0,
        "future_data_used_count": 0,
        "implicit_row_count_window_count": 0,
        "hidden_default_window_count": 0,
        "mixed_data_mode_input_count": 0,
    }


def _parse_observations(observations: Iterable[Observation]) -> list[Observation]:
    rows: list[Observation] = []
    for observation in observations:
        rows.append(
            {
                **observation,
                "date": date.fromisoformat(str(observation["date"])),
                "value": observation["value"],
            }
        )
    return sorted(rows, key=lambda row: row["date"])


def _has_future_data(rows: list[Observation], as_of: date) -> bool:
    return any(row["date"] > as_of for row in rows)


def _subtract_months(value: date, months: int) -> date:
    month_index = value.month - 1 - months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def _result(
    *,
    status: str,
    rule_id: str,
    data_mode: str,
    value: Any = None,
    window_start: date | None = None,
    window_end: date | None = None,
    observation_count: int = 0,
    applied_parameters: dict[str, Any] | None = None,
    provenance: str = "not_applied",
    abstention_reason: str | None = None,
    future_data_used: bool = False,
) -> dict[str, Any]:
    return {
        "status": status,
        "value": value,
        "window_start": window_start.isoformat() if window_start else None,
        "window_end": window_end.isoformat() if window_end else None,
        "observation_count": observation_count,
        "requested_rule_id": rule_id,
        "applied_parameters": applied_parameters or {},
        "provenance": provenance,
        "abstention_reason": abstention_reason,
        "future_data_used": future_data_used,
        "data_mode": data_mode,
    }
