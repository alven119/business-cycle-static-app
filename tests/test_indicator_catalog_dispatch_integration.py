from __future__ import annotations

import pandas as pd

from business_cycle.indicators.catalog import load_indicator_scoring_specs
from business_cycle.indicators.dispatcher import score_indicator
from business_cycle.indicators.scoring import IndicatorScoreResult


def monthly_frame(values: list[float | int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )


def weekly_frame(values: list[float | int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-03", periods=len(values), freq="W-FRI"),
            "value": values,
        }
    )


def assert_indicator_score_result(result: IndicatorScoreResult) -> None:
    assert isinstance(result, IndicatorScoreResult)
    assert 0.0 <= result.score <= 100.0
    assert 0.0 <= result.confidence <= 1.0


def test_catalog_unemployment_rate_spec_dispatches_with_synthetic_data() -> None:
    specs = load_indicator_scoring_specs("specs/indicator_catalog.yaml")
    observations = monthly_frame([6.0] * 10 + [5.8] * 10 + [5.5] * 10 + [5.2] * 10)

    result = score_indicator(observations, specs["unemployment_rate"])

    assert result.indicator_id == "unemployment_rate"
    assert result.method == "level_percentile_score"
    assert_indicator_score_result(result)


def test_catalog_initial_jobless_claims_spec_dispatches_with_synthetic_data() -> None:
    specs = load_indicator_scoring_specs("specs/indicator_catalog.yaml")
    observations = weekly_frame(
        [
            260,
            258,
            256,
            254,
            252,
            250,
            248,
            246,
            244,
            242,
            240,
            238,
            236,
            234,
            232,
            230,
            228,
            226,
            224,
            222,
            220,
            218,
            216,
            214,
        ]
    )

    result = score_indicator(observations, specs["initial_jobless_claims"])

    assert result.indicator_id == "initial_jobless_claims"
    assert result.method == "moving_average_slope_score"
    assert_indicator_score_result(result)

