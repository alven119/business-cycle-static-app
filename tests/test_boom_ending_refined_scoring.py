from __future__ import annotations

import pandas as pd

from business_cycle.indicators.experimental import (
    credit_spread_velocity_score,
    fed_policy_peak_pause_pressure_score,
    financial_conditions_delta_score,
    yield_curve_lead_time_pressure_score,
)


def test_yield_curve_lead_time_pressure_after_sustained_inversion_scores_high() -> None:
    frame = monthly_series([1.0] * 60 + [-0.4] * 12 + [0.2] * 6)

    score = yield_curve_lead_time_pressure_score(frame, as_of="2021-06-30")

    assert score.score is not None
    assert score.score >= 75
    assert score.confidence >= 0.5
    assert score.metadata["lead_time_window_active"] is True


def test_yield_curve_single_inversion_does_not_have_high_confidence() -> None:
    frame = monthly_series([1.0] * 77 + [-0.2])

    score = yield_curve_lead_time_pressure_score(frame, as_of="2021-06-30")

    assert score.confidence < 0.5


def test_yield_curve_old_inversion_outside_window_does_not_stay_high() -> None:
    frame = monthly_series([1.0] * 30 + [-0.4] * 12 + [0.5] * 36)

    score = yield_curve_lead_time_pressure_score(frame, as_of="2021-06-30")

    assert score.metadata["lead_time_window_active"] is False
    assert score.score is not None
    assert score.score < 70


def test_credit_spread_velocity_widening_scores_high_and_marks_selected_spread() -> None:
    primary = monthly_series([1.0] * 80 + [1.0 + i * 0.08 for i in range(20)])
    alternative = monthly_series([0.7] * 80 + [0.7 + i * 0.04 for i in range(20)])

    score = credit_spread_velocity_score(primary, alternative, as_of="2023-04-30")

    assert score.score is not None
    assert score.score >= 65
    assert score.metadata["selected_spread"] in {"BAA - AAA", "BAA - DGS10"}
    assert "alternative_spreads_checked" in score.metadata


def test_financial_conditions_delta_deterioration_scores_high() -> None:
    frame = monthly_series([0.0] * 80 + [i * 0.08 for i in range(20)])

    score = financial_conditions_delta_score(frame, as_of="2023-04-30")

    assert score.score is not None
    assert score.score >= 60
    assert score.metadata["delta"] > 0


def test_fed_policy_peak_pause_pressure_detects_high_pause_after_hikes() -> None:
    frame = monthly_series([0.5] * 30 + [0.5 + i * 0.2 for i in range(18)] + [4.0] * 12)

    score = fed_policy_peak_pause_pressure_score(frame, as_of="2019-12-31")

    assert score.score is not None
    assert score.score >= 65
    assert score.metadata["recent_hike_amount"] > 0


def test_refined_scoring_insufficient_data_lowers_confidence() -> None:
    frame = monthly_series([1.0, -0.2, 0.1])

    score = yield_curve_lead_time_pressure_score(frame, as_of="2015-03-31")

    assert score.confidence < 0.4


def monthly_series(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2015-01-31", periods=len(values), freq="ME"),
            "value": values,
        }
    )
