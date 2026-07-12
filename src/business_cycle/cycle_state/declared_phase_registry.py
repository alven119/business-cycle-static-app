"""Declared current cycle phase registry.

This module exposes a user/governance-declared cycle state. It intentionally
does not infer the current phase from current data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.ordered_state_machine import (
    OrderedCycleStateMachine,
    PHASES,
    load_ordered_cycle_state_machine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_PATH = ROOT / "specs/common/declared_cycle_state_registry.yaml"


class DeclaredCycleStateRegistryError(ValueError):
    """Raised when the declared cycle state registry is invalid."""


@dataclass(frozen=True)
class DeclaredCycleState:
    """Declared cycle state with legal transition context."""

    registry_id: str
    registry_version: str
    declared_current_phase: str
    declared_phase_start_date: date | None
    declared_phase_start_date_status: str
    declared_phase_age: int | None
    phase_age_status: str
    declaration_source: str
    declaration_status: str
    legal_previous_phase: str
    legal_next_phase: str
    formal_current_phase_inference_enabled: bool
    candidate_phase_emission_enabled: bool
    current_phase_emission_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a stable output dictionary for scripts and view models."""

        return {
            "registry_id": self.registry_id,
            "registry_version": self.registry_version,
            "declared_current_phase": self.declared_current_phase,
            "declared_phase_start_date": (
                self.declared_phase_start_date.isoformat()
                if self.declared_phase_start_date is not None
                else None
            ),
            "declared_phase_start_date_status": self.declared_phase_start_date_status,
            "declared_phase_age": self.declared_phase_age,
            "phase_age_status": self.phase_age_status,
            "declaration_source": self.declaration_source,
            "declaration_status": self.declaration_status,
            "legal_previous_phase": self.legal_previous_phase,
            "legal_next_phase": self.legal_next_phase,
            "formal_current_phase_inference_enabled": (
                self.formal_current_phase_inference_enabled
            ),
            "candidate_phase_emission_enabled": self.candidate_phase_emission_enabled,
            "current_phase_emission_enabled": self.current_phase_emission_enabled,
        }


def load_declared_cycle_state(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    *,
    as_of: date | None = None,
    state_machine: OrderedCycleStateMachine | None = None,
) -> DeclaredCycleState:
    """Load the declared cycle state registry without using current data."""

    payload = _load_yaml(registry_path)
    registry = payload["declared_cycle_state_registry"]
    declared = registry["declared_state"]
    semantics = registry["registry_semantics"]
    state_machine = state_machine or load_ordered_cycle_state_machine()

    declared_phase = str(declared["declared_current_phase"])
    start_date = _parse_optional_date(declared["declared_phase_start_date"])
    declared_phase_age = _phase_age(start_date, as_of)
    phase_age_status = (
        "known"
        if declared_phase_age is not None
        else str(declared["phase_age_status"])
    )
    legal_previous_phase = state_machine.legal_previous_phase(declared_phase)
    legal_next_phase = state_machine.legal_next_phase(declared_phase)

    state = DeclaredCycleState(
        registry_id=str(registry["registry_id"]),
        registry_version=str(registry["registry_version"]),
        declared_current_phase=declared_phase,
        declared_phase_start_date=start_date,
        declared_phase_start_date_status=str(declared["declared_phase_start_date_status"]),
        declared_phase_age=declared_phase_age,
        phase_age_status=phase_age_status,
        declaration_source=str(declared["declaration_source"]),
        declaration_status=str(declared["declaration_status"]),
        legal_previous_phase=legal_previous_phase,
        legal_next_phase=legal_next_phase,
        formal_current_phase_inference_enabled=bool(
            semantics["formal_current_phase_inference_enabled"]
        ),
        candidate_phase_emission_enabled=bool(
            semantics["candidate_phase_emission_enabled"]
        ),
        current_phase_emission_enabled=bool(semantics["current_phase_emission_enabled"]),
    )
    _validate_state(state)
    return state


def summarize_declared_cycle_state(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Summarize Phase45 hard gates for declared state."""

    state = load_declared_cycle_state(registry_path)
    phase_age_false_precision_count = (
        0
        if state.declared_phase_start_date is not None
        or (
            state.declared_phase_age is None
            and state.phase_age_status == "unknown_or_user_required"
        )
        else 1
    )
    summary = {
        **state.to_dict(),
        "declared_cycle_state_registry_ready": True,
        "phase_age_contract_ready": phase_age_false_precision_count == 0,
        "phase_age_false_precision_count": phase_age_false_precision_count,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    summary["result"] = "passed" if _summary_passed(summary) else "blocked"
    return summary


def _load_yaml(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as yaml_file:
        payload = yaml.safe_load(yaml_file)
    if not isinstance(payload, dict):
        raise DeclaredCycleStateRegistryError(f"Registry must be a mapping: {registry_path}")
    return payload


def _parse_optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise DeclaredCycleStateRegistryError("declared_phase_start_date must be null or ISO date")


def _phase_age(start_date: date | None, as_of: date | None) -> int | None:
    if start_date is None:
        return None
    as_of = as_of or date.today()
    return max(0, (as_of - start_date).days)


def _validate_state(state: DeclaredCycleState) -> None:
    if state.declared_current_phase not in PHASES:
        raise DeclaredCycleStateRegistryError("Declared phase must be in legal cycle")
    if state.legal_next_phase == state.declared_current_phase:
        raise DeclaredCycleStateRegistryError("Legal next phase cannot equal declared phase")
    if state.formal_current_phase_inference_enabled:
        raise DeclaredCycleStateRegistryError("Formal inference must remain disabled")
    if state.candidate_phase_emission_enabled or state.current_phase_emission_enabled:
        raise DeclaredCycleStateRegistryError("Candidate/current phase emission must remain disabled")


def _summary_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["declared_cycle_state_registry_ready"] is True
        and summary["declared_current_phase"] == "boom"
        and summary["legal_next_phase"] == "recession"
        and summary["phase_age_contract_ready"] is True
        and summary["phase_age_false_precision_count"] == 0
        and summary["current_data_used_to_infer_declared_phase_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
    )
