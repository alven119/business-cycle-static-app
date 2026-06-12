"""Load indicator catalog YAML and build scoring specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.indicators.specs import IndicatorScoringSpec


class IndicatorCatalogError(ValueError):
    """Raised when the indicator catalog cannot be loaded or validated."""


REQUIRED_SCORING_FIELDS = ("indicator_id", "score_method", "direction")


def load_indicator_catalog(path: str | Path) -> list[dict[str, Any]]:
    """Load an indicator catalog from YAML.

    Supports either a top-level list or a mapping with ``indicators: [...]``.
    """

    catalog_path = Path(path)
    if not catalog_path.exists():
        raise IndicatorCatalogError(f"Indicator catalog file does not exist: {catalog_path}")

    try:
        with catalog_path.open("r", encoding="utf-8") as yaml_file:
            payload = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        raise IndicatorCatalogError(f"Invalid YAML in indicator catalog {catalog_path}: {exc}") from exc

    if isinstance(payload, list):
        entries = payload
    elif isinstance(payload, dict) and isinstance(payload.get("indicators"), list):
        entries = payload["indicators"]
    else:
        raise IndicatorCatalogError(
            "Indicator catalog must be a list or a mapping with an 'indicators' list"
        )

    if not all(isinstance(entry, dict) for entry in entries):
        raise IndicatorCatalogError("Every indicator catalog entry must be a mapping")

    return entries


def build_scoring_spec(entry: dict[str, Any]) -> IndicatorScoringSpec:
    """Build an ``IndicatorScoringSpec`` from one catalog entry."""

    missing = [field for field in REQUIRED_SCORING_FIELDS if not entry.get(field)]
    if missing:
        missing_text = ", ".join(missing)
        raise IndicatorCatalogError(f"Indicator catalog entry missing required field(s): {missing_text}")

    parameters = entry.get("parameters", {})
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, dict):
        raise IndicatorCatalogError(
            f"Indicator {entry['indicator_id']!r} field 'parameters' must be a mapping"
        )

    return IndicatorScoringSpec(
        indicator_id=str(entry["indicator_id"]),
        score_method=str(entry["score_method"]),
        direction=str(entry["direction"]),
        value_column=str(entry.get("value_column", "value")),
        date_column=str(entry.get("date_column", "date")),
        parameters=dict(parameters),
        stale_after_days=_optional_int(entry.get("stale_after_days")),
        public_explanation_zh=_optional_str(entry.get("public_explanation_zh")),
    )


def load_indicator_scoring_specs(path: str | Path) -> dict[str, IndicatorScoringSpec]:
    """Load scoring specs keyed by indicator ID."""

    specs: dict[str, IndicatorScoringSpec] = {}
    for entry in load_indicator_catalog(path):
        spec = build_scoring_spec(entry)
        if spec.indicator_id in specs:
            raise IndicatorCatalogError(f"Duplicate indicator_id in catalog: {spec.indicator_id}")
        specs[spec.indicator_id] = spec
    return specs


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
