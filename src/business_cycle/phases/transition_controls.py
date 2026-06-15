"""Experimental phase transition controls for calibration backtests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class TransitionControlsConfigError(ValueError):
    """Raised when transition controls config is invalid."""


@dataclass(frozen=True)
class TransitionWatchRequiredControl:
    enabled: bool = False
    description_zh: str = ""


@dataclass(frozen=True)
class ConfirmationPeriodControl:
    enabled: bool = False
    required_periods: int = 1
    description_zh: str = ""


@dataclass(frozen=True)
class HysteresisMarginControl:
    enabled: bool = False
    min_score_margin: float = 0.0
    description_zh: str = ""


@dataclass(frozen=True)
class CooldownPeriodControl:
    enabled: bool = False
    periods_after_confirmed: int = 0
    description_zh: str = ""


@dataclass(frozen=True)
class BreadthConfirmationControl:
    enabled: bool = False
    target_phases: list[str] = field(default_factory=list)
    min_group_count: int = 1
    min_core_group_count: int = 0
    min_indicator_count: int = 1
    min_phase_signal_score: float = 0.0
    min_indicator_confidence: float = 0.0
    required_groups: list[str] = field(default_factory=list)
    allowed_groups: list[str] = field(default_factory=list)
    core_groups: list[str] = field(default_factory=list)
    non_core_groups: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    description_zh: str = ""


@dataclass(frozen=True)
class TransitionControlsConfig:
    """Feature-gated transition controls for experiments."""

    version: int
    enabled: bool
    description_zh: str
    transition_watch_required: TransitionWatchRequiredControl
    confirmation_period: ConfirmationPeriodControl
    hysteresis_margin: HysteresisMarginControl
    cooldown_period: CooldownPeriodControl
    breadth_confirmation: BreadthConfirmationControl
    caveats_zh: list[str]
    extra_controls: dict[str, Any] = field(default_factory=dict)


def load_transition_controls_config(path: str | Path) -> TransitionControlsConfig:
    """Load transition controls YAML config."""

    payload = _load_yaml_mapping(path)
    config = payload.get("transition_controls")
    if not isinstance(config, dict):
        raise TransitionControlsConfigError("transition_controls YAML must contain a transition_controls mapping")
    controls = config.get("controls")
    if not isinstance(controls, dict):
        raise TransitionControlsConfigError("transition_controls.controls must be a mapping")
    result = TransitionControlsConfig(
        version=int(config.get("version") or 0),
        enabled=_bool(config.get("enabled"), "enabled"),
        description_zh=str(config.get("description_zh") or ""),
        transition_watch_required=_transition_watch_required(controls.get("transition_watch_required")),
        confirmation_period=_confirmation_period(controls.get("confirmation_period")),
        hysteresis_margin=_hysteresis_margin(controls.get("hysteresis_margin")),
        cooldown_period=_cooldown_period(controls.get("cooldown_period")),
        breadth_confirmation=_breadth_confirmation(controls.get("breadth_confirmation")),
        caveats_zh=_str_list(config.get("caveats_zh"), "caveats_zh"),
        extra_controls={key: value for key, value in controls.items() if key not in _KNOWN_CONTROLS},
    )
    validate_transition_controls_config(result)
    return result


def validate_transition_controls_config(config: TransitionControlsConfig) -> None:
    """Validate transition controls config."""

    if config.version <= 0:
        raise TransitionControlsConfigError("version must exist")
    if not isinstance(config.enabled, bool):
        raise TransitionControlsConfigError("enabled must be bool")
    if config.confirmation_period.required_periods < 1:
        raise TransitionControlsConfigError("confirmation_period.required_periods must be >= 1")
    if config.hysteresis_margin.min_score_margin < 0:
        raise TransitionControlsConfigError("hysteresis_margin.min_score_margin must be >= 0")
    if config.cooldown_period.periods_after_confirmed < 0:
        raise TransitionControlsConfigError("cooldown_period.periods_after_confirmed must be >= 0")
    if config.breadth_confirmation.min_group_count < 1:
        raise TransitionControlsConfigError("breadth_confirmation.min_group_count must be >= 1")
    if config.breadth_confirmation.min_core_group_count < 0:
        raise TransitionControlsConfigError("breadth_confirmation.min_core_group_count must be >= 0")
    if config.breadth_confirmation.min_indicator_count < 1:
        raise TransitionControlsConfigError("breadth_confirmation.min_indicator_count must be >= 1")
    if not 0 <= config.breadth_confirmation.min_phase_signal_score <= 100:
        raise TransitionControlsConfigError("breadth_confirmation.min_phase_signal_score must be between 0 and 100")
    if not 0 <= config.breadth_confirmation.min_indicator_confidence <= 1:
        raise TransitionControlsConfigError("breadth_confirmation.min_indicator_confidence must be between 0 and 1")
    if config.breadth_confirmation.enabled and not config.breadth_confirmation.target_phases:
        raise TransitionControlsConfigError("breadth_confirmation.target_phases must not be empty when enabled")
    if config.breadth_confirmation.enabled and not config.breadth_confirmation.allowed_groups:
        raise TransitionControlsConfigError("breadth_confirmation.allowed_groups must not be empty when enabled")
    allowed_groups = set(config.breadth_confirmation.allowed_groups)
    required_groups = set(config.breadth_confirmation.required_groups)
    core_groups = set(config.breadth_confirmation.core_groups)
    non_core_groups = set(config.breadth_confirmation.non_core_groups)
    if not required_groups <= allowed_groups:
        raise TransitionControlsConfigError("breadth_confirmation.required_groups must be a subset of allowed_groups")
    if core_groups and not core_groups <= allowed_groups:
        raise TransitionControlsConfigError("breadth_confirmation.core_groups must be a subset of allowed_groups")
    if non_core_groups and not non_core_groups <= allowed_groups:
        raise TransitionControlsConfigError("breadth_confirmation.non_core_groups must be a subset of allowed_groups")
    overlap = sorted(core_groups & non_core_groups)
    if overlap:
        raise TransitionControlsConfigError(
            f"breadth_confirmation.core_groups and non_core_groups must not overlap: {', '.join(overlap)}"
        )
    if core_groups and config.breadth_confirmation.min_core_group_count > len(core_groups):
        raise TransitionControlsConfigError(
            "breadth_confirmation.min_core_group_count must be <= len(core_groups)"
        )
    if not any("修訂後歷史資料" in caveat for caveat in config.caveats_zh):
        raise TransitionControlsConfigError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in config.caveats_zh):
        raise TransitionControlsConfigError("caveats_zh must include no-investment-advice caveat")


def _transition_watch_required(value: Any) -> TransitionWatchRequiredControl:
    data = _mapping(value)
    return TransitionWatchRequiredControl(
        enabled=_bool(data.get("enabled", False), "transition_watch_required.enabled"),
        description_zh=str(data.get("description_zh") or ""),
    )


def _confirmation_period(value: Any) -> ConfirmationPeriodControl:
    data = _mapping(value)
    return ConfirmationPeriodControl(
        enabled=_bool(data.get("enabled", False), "confirmation_period.enabled"),
        required_periods=int(data["required_periods"]) if "required_periods" in data else 1,
        description_zh=str(data.get("description_zh") or ""),
    )


def _hysteresis_margin(value: Any) -> HysteresisMarginControl:
    data = _mapping(value)
    return HysteresisMarginControl(
        enabled=_bool(data.get("enabled", False), "hysteresis_margin.enabled"),
        min_score_margin=float(data["min_score_margin"]) if "min_score_margin" in data else 0.0,
        description_zh=str(data.get("description_zh") or ""),
    )


def _cooldown_period(value: Any) -> CooldownPeriodControl:
    data = _mapping(value)
    return CooldownPeriodControl(
        enabled=_bool(data.get("enabled", False), "cooldown_period.enabled"),
        periods_after_confirmed=int(data["periods_after_confirmed"]) if "periods_after_confirmed" in data else 0,
        description_zh=str(data.get("description_zh") or ""),
    )


def _breadth_confirmation(value: Any) -> BreadthConfirmationControl:
    data = _mapping(value)
    allowed_groups = _str_list(data.get("allowed_groups"), "breadth_confirmation.allowed_groups", allow_empty=True)
    legacy_groups = _str_list(data.get("groups"), "breadth_confirmation.groups", allow_empty=True)
    return BreadthConfirmationControl(
        enabled=_bool(data.get("enabled", False), "breadth_confirmation.enabled"),
        target_phases=_str_list(data.get("target_phases"), "breadth_confirmation.target_phases", allow_empty=True),
        min_group_count=int(data["min_group_count"]) if "min_group_count" in data else 1,
        min_core_group_count=int(data["min_core_group_count"]) if "min_core_group_count" in data else 0,
        min_indicator_count=int(data["min_indicator_count"]) if "min_indicator_count" in data else 1,
        min_phase_signal_score=(
            float(data["min_phase_signal_score"]) if "min_phase_signal_score" in data else 0.0
        ),
        min_indicator_confidence=(
            float(data["min_indicator_confidence"]) if "min_indicator_confidence" in data else 0.0
        ),
        required_groups=_str_list(data.get("required_groups"), "breadth_confirmation.required_groups", allow_empty=True),
        allowed_groups=allowed_groups or legacy_groups,
        core_groups=_str_list(data.get("core_groups"), "breadth_confirmation.core_groups", allow_empty=True),
        non_core_groups=_str_list(data.get("non_core_groups"), "breadth_confirmation.non_core_groups", allow_empty=True),
        groups=legacy_groups,
        description_zh=str(data.get("description_zh") or ""),
    )


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise TransitionControlsConfigError(f"Transition controls config does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TransitionControlsConfigError(f"Invalid YAML in transition controls config {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise TransitionControlsConfigError("Transition controls YAML must be a mapping")
    return payload


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _str_list(value: Any, field: str, allow_empty: bool = False) -> list[str]:
    if value is None and allow_empty:
        return []
    if not isinstance(value, list) or (not value and not allow_empty):
        raise TransitionControlsConfigError(f"{field} must be a list")
    return [str(item) for item in value]


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise TransitionControlsConfigError(f"{field} must be bool")
    return value


_KNOWN_CONTROLS = {
    "transition_watch_required",
    "confirmation_period",
    "hysteresis_margin",
    "cooldown_period",
    "breadth_confirmation",
}
