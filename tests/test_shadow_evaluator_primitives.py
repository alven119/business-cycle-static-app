from __future__ import annotations

from business_cycle.shadow_model.evaluator_primitives import (
    calendar_time_moving_average,
    cross_series_direction_relation,
    directional_change,
    persistence_window,
    record_low_or_high,
    summarize_evaluator_primitive_guards,
    turning_point_candidate,
)


def test_calendar_three_month_window_is_not_row_count() -> None:
    result = calendar_time_moving_average(
        observations=[
            {"date": "2025-12-01", "value": 999},
            {"date": "2026-01-07", "value": 220},
            {"date": "2026-02-04", "value": 210},
            {"date": "2026-03-04", "value": 200},
        ],
        as_of="2026-03-31",
        calendar_months=3,
        minimum_observations=3,
        rule_id="rule::recovery_weekly_claim_noise_filter",
        data_mode="vintage_as_of",
    )

    assert result["status"] == "matched"
    assert result["value"] == 210
    assert result["window_start"] == "2025-12-31"
    assert result["future_data_used"] is False


def test_weekly_irregular_dates_and_missing_week_use_calendar_window() -> None:
    result = calendar_time_moving_average(
        observations=[
            {"date": "2026-01-09", "value": 220},
            {"date": "2026-02-27", "value": 210},
            {"date": "2026-03-27", "value": 200},
        ],
        as_of="2026-03-31",
        calendar_months=3,
        minimum_observations=3,
        rule_id="rule::recovery_weekly_claim_noise_filter",
        data_mode="vintage_as_of",
    )

    assert result["status"] == "matched"
    assert result["observation_count"] == 3


def test_future_data_and_insufficient_lookback_reject_or_abstain() -> None:
    future = calendar_time_moving_average(
        observations=[
            {"date": "2026-03-04", "value": 200},
            {"date": "2026-04-01", "value": 190},
        ],
        as_of="2026-03-31",
        calendar_months=3,
        minimum_observations=2,
        rule_id="rule::recovery_weekly_claim_noise_filter",
        data_mode="vintage_as_of",
    )
    short = calendar_time_moving_average(
        observations=[{"date": "2026-03-04", "value": 200}],
        as_of="2026-03-31",
        calendar_months=3,
        minimum_observations=2,
        rule_id="rule::recovery_weekly_claim_noise_filter",
        data_mode="vintage_as_of",
    )

    assert future["status"] == "rejected"
    assert future["future_data_used"] is False
    assert short["status"] == "abstained"
    assert short["abstention_reason"] == "insufficient_lookback"


def test_other_primitives_abstain_without_hidden_windows() -> None:
    assert record_low_or_high(
        observations=[],
        as_of="2026-03-31",
        direction="low",
        reference_window_start=None,
        rule_id="rule::boom_claims_u_shape",
        data_mode="vintage_as_of",
    )["abstention_reason"] == "reference_window_not_preregistered"
    assert persistence_window(
        observations=[],
        as_of="2026-03-31",
        calendar_quarters=None,
        condition="nonincreasing",
        rule_id="rule::boom_claims_u_shape",
        data_mode="vintage_as_of",
    )["abstention_reason"] == "persistence_period_not_preregistered"
    assert turning_point_candidate(
        observations=[],
        as_of="2026-03-31",
        direction=None,
        lookback_months=None,
        confirmation_months=None,
        rule_id="rule::trough_claims_reversal",
        data_mode="vintage_as_of",
    )["abstention_reason"] == "turning_point_semantics_incomplete"


def test_direction_and_cross_series_are_same_as_of_only() -> None:
    direction = directional_change(
        observations=[
            {"date": "2026-02-28", "value": 2},
            {"date": "2026-03-31", "value": 3},
        ],
        as_of="2026-03-31",
        direction="up",
        minimum_observations=2,
        rule_id="rule::direction",
        data_mode="revised",
    )
    mixed = cross_series_direction_relation(
        left_observations=[],
        right_observations=[],
        as_of="2026-03-31",
        rule_id="rule::cross",
        data_mode="revised",
        left_data_mode="revised",
        right_data_mode="vintage_as_of",
    )

    assert direction["status"] == "matched"
    assert mixed["abstention_reason"] == "mixed_data_mode_input"


def test_primitive_static_guards_are_clean() -> None:
    summary = summarize_evaluator_primitive_guards()

    assert summary["centered_window_usage_count"] == 0
    assert summary["future_data_used_count"] == 0
    assert summary["implicit_row_count_window_count"] == 0
    assert summary["hidden_default_window_count"] == 0
    assert summary["mixed_data_mode_input_count"] == 0
