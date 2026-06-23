from __future__ import annotations

from business_cycle.shadow_model.phase_evidence_primitives import (
    causal_direction,
    causal_turning_point,
    calendar_moving_average,
    phase_evidence_abstention,
    summarize_phase_evidence_primitives,
)


def _rows(values: list[float], *, data_mode: str = "revised") -> list[dict[str, object]]:
    dates = ["2019-10-31", "2019-11-30", "2019-12-31"]
    return [
        {"date": date, "value": value, "data_mode": data_mode}
        for date, value in zip(dates[: len(values)], values, strict=True)
    ]


def test_phase_evidence_primitives_have_complete_contracts() -> None:
    summary = summarize_phase_evidence_primitives()

    assert summary["primitive_count"] == 10
    assert summary["primitive_with_complete_contract_count"] == 10
    assert summary["future_data_usage_count"] == 0
    assert summary["mixed_data_mode_count"] == 0
    assert summary["hidden_default_count"] == 0
    assert summary["implicit_row_window_count"] == 0
    assert summary["missing_zero_fill_count"] == 0


def test_causal_direction_supports_and_rejects_future_data() -> None:
    result = causal_direction(
        observations=_rows([3.0, 2.0, 1.0]),
        as_of="2019-12-31",
        expected_direction="down",
        data_mode="revised",
        rule_id="rule",
        minimum_observations=2,
    )
    assert result["status"] == "matched"

    future = causal_direction(
        observations=[*_rows([3.0, 2.0, 1.0]), {"date": "2020-01-31", "value": 0.0}],
        as_of="2019-12-31",
        expected_direction="down",
        data_mode="revised",
        rule_id="rule",
        minimum_observations=2,
    )
    assert future["status"] == "rejected"
    assert future["abstention_reason"] == "future_data_rejected"


def test_turning_point_requires_three_observations_and_same_mode() -> None:
    insufficient = causal_turning_point(
        observations=_rows([3.0, 2.0])[:2],
        as_of="2019-12-31",
        expected_turn="up",
        data_mode="revised",
        rule_id="turn",
        minimum_observations=3,
    )
    assert insufficient["status"] == "abstained"

    mixed = causal_turning_point(
        observations=[
            {"date": "2019-10-31", "value": 3.0, "data_mode": "revised"},
            {"date": "2019-11-30", "value": 2.0, "data_mode": "vintage_as_of"},
            {"date": "2019-12-31", "value": 4.0, "data_mode": "revised"},
        ],
        as_of="2019-12-31",
        expected_turn="up",
        data_mode="revised",
        rule_id="turn",
        minimum_observations=3,
    )
    assert mixed["status"] == "rejected"
    assert mixed["abstention_reason"] == "mixed_data_mode_rejected"


def test_smoothing_and_abstention_are_not_phase_support() -> None:
    moving_average = calendar_moving_average(
        observations=_rows([1.0, 2.0, 3.0]),
        as_of="2019-12-31",
        calendar_months=3,
        minimum_observations=3,
        data_mode="revised",
        rule_id="ma",
    )
    abstention = phase_evidence_abstention("role", "insufficient_lookback")

    assert moving_average["status"] == "matched"
    assert abstention["current_phase_emitted"] is False
    assert abstention["candidate_selection_eligible"] is False
