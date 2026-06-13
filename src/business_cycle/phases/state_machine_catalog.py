"""Load phase state machine config from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.phases.state_machine import PhaseStateMachineConfig


class PhaseStateMachineConfigError(ValueError):
    """Raised when state machine config cannot be loaded or validated."""


REQUIRED_FIELDS = (
    "phase_order",
    "min_phase_confidence",
    "min_available_weight",
    "min_score_for_initial_estimate",
    "min_score_margin",
    "transition_score_margin",
    "allow_initial_estimate",
)
REQUIRED_PHASES = {"recession", "recovery", "growth", "boom"}


def load_phase_state_machine_config(path: str | Path) -> PhaseStateMachineConfig:
    """Load and validate phase state machine config."""

    config_path = Path(path)
    if not config_path.exists():
        raise PhaseStateMachineConfigError(f"State machine config file does not exist: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as yaml_file:
            payload = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        raise PhaseStateMachineConfigError(
            f"Invalid YAML in state machine config {config_path}: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise PhaseStateMachineConfigError("State machine config must be a mapping")

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise PhaseStateMachineConfigError(
            f"State machine config missing required field(s): {', '.join(missing)}"
        )

    phase_order = _phase_order(payload["phase_order"])
    _validate_probability("min_phase_confidence", payload["min_phase_confidence"])
    _validate_probability("min_available_weight", payload["min_available_weight"])
    _validate_score("min_score_for_initial_estimate", payload["min_score_for_initial_estimate"])
    _validate_score_margin("min_score_margin", payload["min_score_margin"])
    _validate_score_margin("transition_score_margin", payload["transition_score_margin"])

    return PhaseStateMachineConfig(
        phase_order=phase_order,
        min_phase_confidence=float(payload["min_phase_confidence"]),
        min_available_weight=float(payload["min_available_weight"]),
        min_score_for_initial_estimate=float(payload["min_score_for_initial_estimate"]),
        min_score_margin=float(payload["min_score_margin"]),
        transition_score_margin=float(payload["transition_score_margin"]),
        allow_initial_estimate=_bool_value(payload["allow_initial_estimate"]),
    )


def _phase_order(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PhaseStateMachineConfigError("phase_order must be a non-empty list")
    phase_order = [str(item) for item in value]
    missing = sorted(REQUIRED_PHASES - set(phase_order))
    if missing:
        raise PhaseStateMachineConfigError(f"phase_order missing required phase(s): {', '.join(missing)}")
    if len(phase_order) != len(set(phase_order)):
        raise PhaseStateMachineConfigError("phase_order must not contain duplicates")
    return phase_order


def _validate_probability(field: str, value: Any) -> None:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise PhaseStateMachineConfigError(f"{field} must be between 0 and 1")


def _validate_score(field: str, value: Any) -> None:
    number = float(value)
    if not 0.0 <= number <= 100.0:
        raise PhaseStateMachineConfigError(f"{field} must be between 0 and 100")


def _validate_score_margin(field: str, value: Any) -> None:
    number = float(value)
    if not 0.0 <= number <= 100.0:
        raise PhaseStateMachineConfigError(f"{field} must be between 0 and 100")


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raise PhaseStateMachineConfigError("allow_initial_estimate must be a boolean")
