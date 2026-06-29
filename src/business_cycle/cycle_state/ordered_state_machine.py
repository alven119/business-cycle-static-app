"""Ordered legal cycle transition contract for declared cycle state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC_PATH = ROOT / "specs/common/ordered_cycle_state_machine.yaml"
PHASES = ("recession", "recovery", "growth", "boom")


class OrderedCycleStateMachineError(ValueError):
    """Raised when the ordered cycle state-machine contract is invalid."""


@dataclass(frozen=True)
class TransitionOverrideContract:
    """Explicit override metadata for an otherwise illegal transition."""

    approved: bool
    source: str
    reason: str


@dataclass(frozen=True)
class TransitionCheck:
    """Result of checking one requested transition against the legal order."""

    from_phase: str
    to_phase: str
    legal_next_phase: str
    is_legal: bool
    rejection_reason: str | None
    override_used: bool = False


@dataclass(frozen=True)
class OrderedCycleStateMachine:
    """Minimal ordered cycle state machine with no scoring or classifier logic."""

    state_machine_id: str
    state_machine_version: str
    cycle_order: tuple[str, ...]
    legal_transitions: dict[str, str]
    legal_previous_transitions: dict[str, str]
    override_contract_implemented: bool = False

    def legal_next_phase(self, phase: str) -> str:
        """Return the only legal next phase for a declared phase."""

        self._validate_phase(phase)
        return self.legal_transitions[phase]

    def legal_previous_phase(self, phase: str) -> str:
        """Return the legal previous phase for a declared phase."""

        self._validate_phase(phase)
        return self.legal_previous_transitions[phase]

    def check_transition(
        self,
        from_phase: str,
        to_phase: str,
        *,
        override_contract: TransitionOverrideContract | None = None,
    ) -> TransitionCheck:
        """Check whether a requested transition follows the declared legal order."""

        self._validate_phase(from_phase)
        self._validate_phase(to_phase)
        legal_next = self.legal_next_phase(from_phase)
        if to_phase == from_phase:
            return TransitionCheck(
                from_phase=from_phase,
                to_phase=to_phase,
                legal_next_phase=legal_next,
                is_legal=False,
                rejection_reason="self_transition_not_legal_next",
            )
        if to_phase == legal_next:
            return TransitionCheck(
                from_phase=from_phase,
                to_phase=to_phase,
                legal_next_phase=legal_next,
                is_legal=True,
                rejection_reason=None,
            )
        if self._valid_override(override_contract):
            return TransitionCheck(
                from_phase=from_phase,
                to_phase=to_phase,
                legal_next_phase=legal_next,
                is_legal=True,
                rejection_reason=None,
                override_used=True,
            )
        return TransitionCheck(
            from_phase=from_phase,
            to_phase=to_phase,
            legal_next_phase=legal_next,
            is_legal=False,
            rejection_reason="illegal_transition_requires_explicit_override_contract",
        )

    def summary(self) -> dict[str, Any]:
        """Return contract-level audit fields for scripts and tests."""

        illegal_checks = [
            self.check_transition("boom", "boom"),
            self.check_transition("boom", "growth"),
            self.check_transition("recession", "boom"),
        ]
        illegal_rejected_count = sum(not check.is_legal for check in illegal_checks)
        legal_cycle_order_valid = _legal_cycle_order_valid(
            self.cycle_order,
            self.legal_transitions,
            self.legal_previous_transitions,
        )
        return {
            "ordered_cycle_state_machine_ready": legal_cycle_order_valid,
            "state_machine_id": self.state_machine_id,
            "state_machine_version": self.state_machine_version,
            "cycle_order": list(self.cycle_order),
            "legal_transitions": dict(self.legal_transitions),
            "legal_previous_transitions": dict(self.legal_previous_transitions),
            "legal_cycle_order_valid": legal_cycle_order_valid,
            "illegal_transition_rejected_count": illegal_rejected_count,
            "self_transition_rejected": self.check_transition("boom", "boom").is_legal
            is False,
            "legal_transition_semantics_preserved": legal_cycle_order_valid,
            "standalone_classifier_added_count": 0,
            "phase_rank_or_score_added_count": 0,
            "role_count_voting_added_count": 0,
        }

    def _validate_phase(self, phase: str) -> None:
        if phase not in self.cycle_order:
            raise OrderedCycleStateMachineError(f"Unknown cycle phase: {phase}")

    def _valid_override(self, override_contract: TransitionOverrideContract | None) -> bool:
        return (
            self.override_contract_implemented
            and override_contract is not None
            and override_contract.approved
            and bool(override_contract.source)
            and bool(override_contract.reason)
        )


def load_ordered_cycle_state_machine(
    path: str | Path = DEFAULT_SPEC_PATH,
) -> OrderedCycleStateMachine:
    """Load the ordered cycle state machine from its YAML contract."""

    payload = _load_yaml(path)
    contract = payload["ordered_cycle_state_machine"]
    cycle_order = tuple(str(phase) for phase in contract["cycle_order"])
    legal_transitions = {
        str(phase): str(next_phase)
        for phase, next_phase in contract["legal_transitions"].items()
    }
    legal_previous_transitions = {
        str(phase): str(previous_phase)
        for phase, previous_phase in contract["legal_previous_transitions"].items()
    }
    machine = OrderedCycleStateMachine(
        state_machine_id=str(contract["state_machine_id"]),
        state_machine_version=str(contract["state_machine_version"]),
        cycle_order=cycle_order,
        legal_transitions=legal_transitions,
        legal_previous_transitions=legal_previous_transitions,
        override_contract_implemented=bool(
            contract["transition_rules"]["override_contract_implemented_in_phase45"]
        ),
    )
    if not _legal_cycle_order_valid(cycle_order, legal_transitions, legal_previous_transitions):
        raise OrderedCycleStateMachineError("Ordered cycle state machine contract is invalid")
    return machine


def _load_yaml(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    with spec_path.open("r", encoding="utf-8") as yaml_file:
        payload = yaml.safe_load(yaml_file)
    if not isinstance(payload, dict):
        raise OrderedCycleStateMachineError(f"Spec must be a mapping: {spec_path}")
    return payload


def _legal_cycle_order_valid(
    cycle_order: tuple[str, ...],
    legal_transitions: dict[str, str],
    legal_previous_transitions: dict[str, str],
) -> bool:
    if cycle_order != PHASES:
        return False
    if set(legal_transitions) != set(PHASES):
        return False
    if set(legal_previous_transitions) != set(PHASES):
        return False
    for index, phase in enumerate(cycle_order):
        next_phase = cycle_order[(index + 1) % len(cycle_order)]
        previous_phase = cycle_order[(index - 1) % len(cycle_order)]
        if legal_transitions[phase] != next_phase:
            return False
        if legal_previous_transitions[phase] != previous_phase:
            return False
        if legal_transitions[phase] == phase:
            return False
    return True
