"""Load phase scoring specs from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.phases.specs import PhaseIndicatorWeight, PhaseScoringSpec


class PhaseCatalogError(ValueError):
    """Raised when a phase spec cannot be loaded or validated."""


REQUIRED_PHASE_FIELDS = (
    "phase_id",
    "phase_name_zh",
    "description_zh",
    "indicators",
    "minimum_available_weight",
    "confidence_policy",
    "early_mid_late_thresholds",
)

VALID_ROLES = {"core", "confirmation", "warning", "optional"}


def load_phase_spec(path: str | Path) -> PhaseScoringSpec:
    """Load one phase scoring spec from YAML."""

    spec_path = Path(path)
    if not spec_path.exists():
        raise PhaseCatalogError(f"Phase spec file does not exist: {spec_path}")

    try:
        with spec_path.open("r", encoding="utf-8") as yaml_file:
            payload = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        raise PhaseCatalogError(f"Invalid YAML in phase spec {spec_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise PhaseCatalogError(f"Phase spec {spec_path} must be a mapping")

    missing = [field for field in REQUIRED_PHASE_FIELDS if field not in payload]
    if missing:
        missing_text = ", ".join(missing)
        raise PhaseCatalogError(f"Phase spec {spec_path} missing required field(s): {missing_text}")

    minimum_available_weight = float(payload["minimum_available_weight"])
    if not 0.0 <= minimum_available_weight <= 1.0:
        raise PhaseCatalogError("minimum_available_weight must be between 0 and 1")

    indicators = _build_indicator_weights(payload["indicators"])
    raw_total_weight = sum(indicator.weight for indicator in indicators)
    normalized_indicators = [
        PhaseIndicatorWeight(
            indicator_id=indicator.indicator_id,
            weight=indicator.weight / raw_total_weight,
            role=indicator.role,
            direction_note_zh=indicator.direction_note_zh,
        )
        for indicator in indicators
    ]

    thresholds = payload["early_mid_late_thresholds"]
    if not isinstance(thresholds, dict):
        raise PhaseCatalogError("early_mid_late_thresholds must be a mapping")

    confidence_policy = payload["confidence_policy"]
    if not isinstance(confidence_policy, dict):
        raise PhaseCatalogError("confidence_policy must be a mapping")

    return PhaseScoringSpec(
        phase_id=str(payload["phase_id"]),
        phase_name_zh=str(payload["phase_name_zh"]),
        description_zh=str(payload["description_zh"]),
        indicators=normalized_indicators,
        minimum_available_weight=minimum_available_weight,
        confidence_policy=dict(confidence_policy),
        early_mid_late_thresholds={str(key): float(value) for key, value in thresholds.items()},
        transition_watch=_optional_dict(payload.get("transition_watch")),
        public_explanation_zh=_optional_str(payload.get("public_explanation_zh")),
        details={"raw_total_weight": raw_total_weight, "source_path": str(spec_path)},
    )


def load_phase_specs(path: str | Path) -> dict[str, PhaseScoringSpec]:
    """Load phase specs from a YAML file or all YAML files in a directory."""

    spec_path = Path(path)
    paths = _phase_spec_paths(spec_path)
    specs: dict[str, PhaseScoringSpec] = {}
    for phase_path in paths:
        spec = load_phase_spec(phase_path)
        if spec.phase_id in specs:
            raise PhaseCatalogError(f"Duplicate phase_id: {spec.phase_id}")
        specs[spec.phase_id] = spec
    return specs


def _build_indicator_weights(raw_indicators: Any) -> list[PhaseIndicatorWeight]:
    if not isinstance(raw_indicators, list) or not raw_indicators:
        raise PhaseCatalogError("indicators must be a non-empty list")

    indicators: list[PhaseIndicatorWeight] = []
    for raw_indicator in raw_indicators:
        if not isinstance(raw_indicator, dict):
            raise PhaseCatalogError("Each phase indicator must be a mapping")
        indicator_id = raw_indicator.get("indicator_id")
        if not indicator_id:
            raise PhaseCatalogError("Each phase indicator must include indicator_id")
        weight = float(raw_indicator.get("weight", 0.0))
        if weight <= 0.0:
            raise PhaseCatalogError(f"Indicator {indicator_id!r} weight must be > 0")
        role = _optional_str(raw_indicator.get("role"))
        if role is not None and role not in VALID_ROLES:
            allowed = ", ".join(sorted(VALID_ROLES))
            raise PhaseCatalogError(f"Indicator {indicator_id!r} role must be one of: {allowed}")
        indicators.append(
            PhaseIndicatorWeight(
                indicator_id=str(indicator_id),
                weight=weight,
                role=role,
                direction_note_zh=_optional_str(raw_indicator.get("direction_note_zh")),
            )
        )

    raw_total_weight = sum(indicator.weight for indicator in indicators)
    if raw_total_weight <= 0.0:
        raise PhaseCatalogError("Total indicator weight must be > 0")
    return indicators


def _phase_spec_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted([*path.glob("*.yaml"), *path.glob("*.yml")])
    raise PhaseCatalogError(f"Phase spec path does not exist: {path}")


def _optional_dict(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise PhaseCatalogError("transition_watch must be a mapping when provided")
    return dict(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)

