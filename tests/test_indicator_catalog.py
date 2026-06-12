from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.indicators.catalog import (
    IndicatorCatalogError,
    build_scoring_spec,
    load_indicator_catalog,
    load_indicator_scoring_specs,
)
from business_cycle.indicators.specs import IndicatorScoringSpec


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_indicator_catalog_supports_list_format(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "catalog.yaml",
        """
- indicator_id: x
  score_method: level_percentile_score
  direction: higher_is_better
""",
    )

    entries = load_indicator_catalog(path)

    assert entries[0]["indicator_id"] == "x"


def test_load_indicator_catalog_supports_indicators_mapping_format(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "catalog.yaml",
        """
indicators:
  - indicator_id: x
    score_method: level_percentile_score
    direction: higher_is_better
""",
    )

    entries = load_indicator_catalog(path)

    assert entries[0]["indicator_id"] == "x"


def test_missing_catalog_file_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(IndicatorCatalogError, match="does not exist"):
        load_indicator_catalog(tmp_path / "missing.yaml")


def test_invalid_yaml_raises_clear_error(tmp_path: Path) -> None:
    path = write_yaml(tmp_path / "catalog.yaml", "indicators: [\n")

    with pytest.raises(IndicatorCatalogError, match="Invalid YAML"):
        load_indicator_catalog(path)


def test_missing_indicator_id_raises_clear_error() -> None:
    with pytest.raises(IndicatorCatalogError, match="indicator_id"):
        build_scoring_spec({"score_method": "level_percentile_score", "direction": "higher_is_better"})


def test_missing_score_method_raises_clear_error() -> None:
    with pytest.raises(IndicatorCatalogError, match="score_method"):
        build_scoring_spec({"indicator_id": "x", "direction": "higher_is_better"})


def test_missing_direction_raises_clear_error() -> None:
    with pytest.raises(IndicatorCatalogError, match="direction"):
        build_scoring_spec({"indicator_id": "x", "score_method": "level_percentile_score"})


def test_duplicate_indicator_id_raises_clear_error(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "catalog.yaml",
        """
indicators:
  - indicator_id: x
    score_method: level_percentile_score
    direction: higher_is_better
  - indicator_id: x
    score_method: moving_average_slope_score
    direction: rising_is_better
""",
    )

    with pytest.raises(IndicatorCatalogError, match="Duplicate indicator_id"):
        load_indicator_scoring_specs(path)


def test_build_scoring_spec_builds_indicator_scoring_spec() -> None:
    spec = build_scoring_spec(
        {
            "indicator_id": "x",
            "score_method": "yoy_momentum_score",
            "direction": "higher_is_better",
            "value_column": "raw_value",
            "date_column": "observation_date",
            "parameters": {"periods": 12},
            "stale_after_days": 45,
            "public_explanation_zh": "測試說明",
        }
    )

    assert spec == IndicatorScoringSpec(
        indicator_id="x",
        score_method="yoy_momentum_score",
        direction="higher_is_better",
        value_column="raw_value",
        date_column="observation_date",
        parameters={"periods": 12},
        stale_after_days=45,
        public_explanation_zh="測試說明",
    )


def test_load_indicator_scoring_specs_returns_dict(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "catalog.yaml",
        """
indicators:
  - indicator_id: x
    score_method: level_percentile_score
    direction: higher_is_better
""",
    )

    specs = load_indicator_scoring_specs(path)

    assert list(specs) == ["x"]
    assert isinstance(specs["x"], IndicatorScoringSpec)


def test_project_indicator_catalog_loads() -> None:
    entries = load_indicator_catalog("specs/indicator_catalog.yaml")

    assert len(entries) >= 4


def test_project_catalog_minimum_four_indicators_build_scoring_specs() -> None:
    specs = load_indicator_scoring_specs("specs/indicator_catalog.yaml")

    for indicator_id in [
        "unemployment_rate",
        "initial_jobless_claims",
        "real_retail_sales",
        "durable_goods_orders",
    ]:
        assert indicator_id in specs
        assert isinstance(specs[indicator_id], IndicatorScoringSpec)

