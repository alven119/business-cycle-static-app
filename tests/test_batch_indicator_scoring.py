from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from business_cycle.indicators.batch_scoring import (
    score_indicator_batch,
    serialize_indicator_score_result,
    write_indicator_scores_json,
)
from business_cycle.indicators.specs import IndicatorScoringSpec


def monthly_frame(values: list[float | int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )


def specs() -> dict[str, IndicatorScoringSpec]:
    return {
        "b_indicator": IndicatorScoringSpec(
            indicator_id="b_indicator",
            score_method="moving_average_slope_score",
            direction="rising_is_better",
            parameters={"moving_average_window": 2, "slope_window": 3, "confirmation_window": 2},
        ),
        "a_indicator": IndicatorScoringSpec(
            indicator_id="a_indicator",
            score_method="level_percentile_score",
            direction="higher_is_better",
            parameters={"min_periods": 3},
        ),
    }


def test_batch_scoring_scores_multiple_indicators() -> None:
    summary = score_indicator_batch(
        {
            "a_indicator": monthly_frame([1, 2, 3, 4]),
            "b_indicator": monthly_frame([1, 2, 3, 4, 5, 6]),
        },
        specs(),
    )

    assert summary.total_indicators == 2
    assert summary.scored_indicators == 2
    assert summary.failed_indicators == 0


def test_single_indicator_failure_does_not_stop_batch() -> None:
    bad_specs = {
        **specs(),
        "c_indicator": IndicatorScoringSpec(
            indicator_id="c_indicator",
            score_method="unknown",
            direction="higher_is_better",
        ),
    }
    summary = score_indicator_batch(
        {
            "a_indicator": monthly_frame([1, 2, 3, 4]),
            "b_indicator": monthly_frame([1, 2, 3, 4, 5, 6]),
            "c_indicator": monthly_frame([1, 2, 3]),
        },
        bad_specs,
    )

    assert summary.scored_indicators == 2
    assert summary.failed_indicators == 1
    assert summary.failures[0]["indicator_id"] == "c_indicator"


def test_results_are_ordered_by_indicator_id() -> None:
    summary = score_indicator_batch(
        {
            "a_indicator": monthly_frame([1, 2, 3, 4]),
            "b_indicator": monthly_frame([1, 2, 3, 4, 5, 6]),
        },
        specs(),
    )

    assert [result.indicator_id for result in summary.results] == ["a_indicator", "b_indicator"]


def test_as_of_prevents_future_data_use() -> None:
    base = monthly_frame([1, 2, 3, 4, 5, 6])
    future = monthly_frame([1, 2, 3, 4, 5, 6, 1000, 2000])
    selected_specs = {"b_indicator": specs()["b_indicator"]}

    first = score_indicator_batch({"b_indicator": base}, selected_specs, as_of="2020-06-01")
    second = score_indicator_batch({"b_indicator": future}, selected_specs, as_of="2020-06-01")

    assert second.results[0].score == first.results[0].score
    assert second.results[0].confidence == first.results[0].confidence


def test_failure_contains_indicator_id_error_type_and_message() -> None:
    summary = score_indicator_batch({}, {"a_indicator": specs()["a_indicator"]})

    assert summary.failures == [
        {
            "indicator_id": "a_indicator",
            "error_type": "MissingObservations",
            "message": "No observations provided for indicator 'a_indicator'.",
        }
    ]


def test_serialize_indicator_score_result_is_json_serializable() -> None:
    summary = score_indicator_batch(
        {"a_indicator": monthly_frame([1, 2, 3, 4])},
        {"a_indicator": specs()["a_indicator"]},
    )
    payload = serialize_indicator_score_result(summary.results[0])

    json.dumps(payload)
    assert payload["indicator_id"] == "a_indicator"


def test_write_indicator_scores_json_writes_file(tmp_path: Path) -> None:
    summary = score_indicator_batch(
        {"a_indicator": monthly_frame([1, 2, 3, 4])},
        {"a_indicator": specs()["a_indicator"]},
    )
    output_path = write_indicator_scores_json(summary, tmp_path / "scores.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"] == {
        "total_indicators": 1,
        "scored_indicators": 1,
        "failed_indicators": 0,
    }
    assert payload["results"][0]["indicator_id"] == "a_indicator"


def test_summary_counts_are_correct() -> None:
    summary = score_indicator_batch(
        {"a_indicator": monthly_frame([1, 2, 3, 4])},
        specs(),
    )

    assert summary.total_indicators == 2
    assert summary.scored_indicators == 1
    assert summary.failed_indicators == 1

