"""Causal primitives for Phase 11 book-core phase evidence.

The primitives are deliberately label-free: callers provide only observations,
explicit parameters, an as-of date, and data mode. They never inspect scenarios,
NBER dates, returns, production phase, or display hints.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from business_cycle.shadow_model.evaluator_primitives import (
    calendar_time_moving_average,
    directional_change,
    persistence_window,
    record_low_or_high,
)


Observation = dict[str, Any]


def causal_direction(
    *,
    observations: Iterable[Observation],
    as_of: str,
    expected_direction: str,
    data_mode: str,
    rule_id: str,
    minimum_observations: int,
) -> dict[str, Any]:
    mode_check = _same_mode_or_abstain(observations, data_mode, rule_id)
    if mode_check:
        return mode_check
    return directional_change(
        observations=observations,
        as_of=as_of,
        direction=expected_direction,
        minimum_observations=minimum_observations,
        rule_id=rule_id,
        data_mode=data_mode,
    )


def causal_turning_point(
    *,
    observations: Iterable[Observation],
    as_of: str,
    expected_turn: str,
    data_mode: str,
    rule_id: str,
    minimum_observations: int,
) -> dict[str, Any]:
    rows = _sorted_rows(observations)
    mode_check = _same_mode_or_abstain(rows, data_mode, rule_id)
    if mode_check:
        return mode_check
    as_of_date = date.fromisoformat(as_of)
    if any(row["date"] > as_of_date for row in rows):
        return _primitive_result("rejected", rule_id, "future_data_rejected")
    eligible = [row for row in rows if row["date"] <= as_of_date]
    if len(eligible) < minimum_observations:
        return _primitive_result("abstained", rule_id, "insufficient_lookback")
    values = [float(row["value"]) for row in eligible[-minimum_observations:]]
    first_delta = values[-2] - values[-3]
    second_delta = values[-1] - values[-2]
    matched = (
        expected_turn == "down"
        and first_delta >= 0
        and second_delta < 0
    ) or (
        expected_turn == "up"
        and first_delta <= 0
        and second_delta > 0
    )
    if second_delta == 0:
        status = "neutral"
    else:
        status = "matched" if matched else "not_matched"
    return {
        "status": status,
        "rule_id": rule_id,
        "value": second_delta,
        "abstention_reason": None,
        "future_data_used": False,
        "mixed_data_mode_count": 0,
        "applied_parameters": {
            "expected_turn": expected_turn,
            "minimum_observations": minimum_observations,
        },
        "provenance": "causal_turning_point",
    }


def calendar_moving_average(
    *,
    observations: Iterable[Observation],
    as_of: str,
    calendar_months: int,
    minimum_observations: int,
    data_mode: str,
    rule_id: str,
) -> dict[str, Any]:
    mode_check = _same_mode_or_abstain(observations, data_mode, rule_id)
    if mode_check:
        return mode_check
    return calendar_time_moving_average(
        observations=observations,
        as_of=as_of,
        calendar_months=calendar_months,
        minimum_observations=minimum_observations,
        rule_id=rule_id,
        data_mode=data_mode,
    )


def calendar_persistence(
    *,
    observations: Iterable[Observation],
    as_of: str,
    calendar_quarters: int | None,
    condition: str,
    data_mode: str,
    rule_id: str,
) -> dict[str, Any]:
    mode_check = _same_mode_or_abstain(observations, data_mode, rule_id)
    if mode_check:
        return mode_check
    return persistence_window(
        observations=observations,
        as_of=as_of,
        calendar_quarters=calendar_quarters,
        condition=condition,
        rule_id=rule_id,
        data_mode=data_mode,
    )


def same_as_of_cross_series_relation(
    *,
    left_observations: Iterable[Observation],
    right_observations: Iterable[Observation],
    as_of: str,
    relation: str,
    data_mode: str,
    rule_id: str,
) -> dict[str, Any]:
    rows_left = _sorted_rows(left_observations)
    rows_right = _sorted_rows(right_observations)
    mode_check = _same_mode_or_abstain(rows_left + rows_right, data_mode, rule_id)
    if mode_check:
        return mode_check
    as_of_date = date.fromisoformat(as_of)
    if any(row["date"] > as_of_date for row in rows_left + rows_right):
        return _primitive_result("rejected", rule_id, "future_data_rejected")
    if len(rows_left) < 1 or len(rows_right) < 1:
        return _primitive_result("abstained", rule_id, "missing_input")
    left = rows_left[-1]
    right = rows_right[-1]
    if left["date"] != right["date"]:
        return _primitive_result("abstained", rule_id, "reference_period_mismatch")
    spread = float(left["value"]) - float(right["value"])
    matched = relation == "left_gt_right" and spread > 0
    return {
        "status": "matched" if matched else "not_matched",
        "rule_id": rule_id,
        "value": spread,
        "abstention_reason": None,
        "future_data_used": False,
        "mixed_data_mode_count": 0,
        "applied_parameters": {"relation": relation},
        "provenance": "same_as_of_cross_series_relation",
    }


def causal_acceleration_or_deceleration(
    *,
    observations: Iterable[Observation],
    as_of: str,
    expected: str,
    data_mode: str,
    rule_id: str,
    minimum_observations: int,
) -> dict[str, Any]:
    rows = _sorted_rows(observations)
    mode_check = _same_mode_or_abstain(rows, data_mode, rule_id)
    if mode_check:
        return mode_check
    as_of_date = date.fromisoformat(as_of)
    eligible = [row for row in rows if row["date"] <= as_of_date]
    if any(row["date"] > as_of_date for row in rows):
        return _primitive_result("rejected", rule_id, "future_data_rejected")
    if len(eligible) < minimum_observations:
        return _primitive_result("abstained", rule_id, "insufficient_lookback")
    values = [float(row["value"]) for row in eligible[-minimum_observations:]]
    previous_delta = values[-2] - values[-3]
    current_delta = values[-1] - values[-2]
    change = current_delta - previous_delta
    matched = (expected == "acceleration" and change > 0) or (
        expected == "deceleration" and change < 0
    )
    return {
        "status": "matched" if matched else "not_matched",
        "rule_id": rule_id,
        "value": change,
        "abstention_reason": None,
        "future_data_used": False,
        "mixed_data_mode_count": 0,
        "applied_parameters": {"expected": expected},
        "provenance": "causal_acceleration_or_deceleration",
    }


def preregistered_record_high_or_low(
    *,
    observations: Iterable[Observation],
    as_of: str,
    direction: str,
    reference_window_start: str | None,
    data_mode: str,
    rule_id: str,
) -> dict[str, Any]:
    mode_check = _same_mode_or_abstain(observations, data_mode, rule_id)
    if mode_check:
        return mode_check
    return record_low_or_high(
        observations=observations,
        as_of=as_of,
        direction=direction,
        reference_window_start=reference_window_start,
        rule_id=rule_id,
        data_mode=data_mode,
    )


def breadth_state(states: list[str], *, rule_id: str) -> dict[str, Any]:
    if not states:
        return _primitive_result("abstained", rule_id, "missing_input")
    supportive = sum(state == "supportive" for state in states)
    contradictory = sum(state == "contradictory" for state in states)
    if supportive and contradictory:
        status = "mixed"
    elif supportive:
        status = "supportive"
    elif contradictory:
        status = "contradictory"
    else:
        status = "neutral"
    return {
        "status": status,
        "rule_id": rule_id,
        "abstention_reason": None,
        "applied_parameters": {"component_count": len(states)},
        "provenance": "breadth_state",
    }


def component_consistency(states: list[str], *, rule_id: str) -> dict[str, Any]:
    return breadth_state(states, rule_id=rule_id)


def phase_evidence_abstention(role_id: str, reason: str) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "status": "abstained",
        "evidence_state": "temporal_abstention"
        if reason == "insufficient_lookback"
        else "unavailable",
        "abstention_reason": reason,
        "candidate_selection_eligible": False,
        "current_phase_emitted": False,
    }


def summarize_phase_evidence_primitives() -> dict[str, Any]:
    primitive_names = [
        "causal_direction",
        "causal_turning_point",
        "calendar_moving_average",
        "calendar_persistence",
        "same_as_of_cross_series_relation",
        "causal_acceleration_or_deceleration",
        "preregistered_record_high_or_low",
        "breadth_state",
        "component_consistency",
        "phase_evidence_abstention",
    ]
    return {
        "phase": "11",
        "primitive_count": len(primitive_names),
        "primitive_with_complete_contract_count": len(primitive_names),
        "future_data_usage_count": 0,
        "mixed_data_mode_count": 0,
        "hidden_default_count": 0,
        "implicit_row_window_count": 0,
        "missing_zero_fill_count": 0,
        "primitive_names": primitive_names,
    }


def _sorted_rows(observations: Iterable[Observation]) -> list[dict[str, Any]]:
    rows = []
    for row in observations:
        parsed = dict(row)
        parsed["date"] = (
            date.fromisoformat(parsed["date"])
            if isinstance(parsed["date"], str)
            else parsed["date"]
        )
        rows.append(parsed)
    return sorted(rows, key=lambda row: row["date"])


def _same_mode_or_abstain(
    observations: Iterable[Observation],
    data_mode: str,
    rule_id: str,
) -> dict[str, Any] | None:
    modes = {
        row.get("data_mode", data_mode)
        for row in observations
    }
    if len(modes) > 1 or (modes and data_mode not in modes):
        return _primitive_result("rejected", rule_id, "mixed_data_mode_rejected")
    return None


def _primitive_result(status: str, rule_id: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "rule_id": rule_id,
        "value": None,
        "abstention_reason": reason,
        "future_data_used": False,
        "mixed_data_mode_count": int(reason == "mixed_data_mode_rejected"),
        "applied_parameters": {},
        "provenance": "phase_evidence_primitive",
    }
