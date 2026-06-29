from __future__ import annotations

from business_cycle.cycle_state.ordered_state_machine import (
    OrderedCycleStateMachineError,
    load_ordered_cycle_state_machine,
)


def test_legal_cycle_order_and_next_previous_phase() -> None:
    machine = load_ordered_cycle_state_machine()

    assert machine.cycle_order == ("recession", "recovery", "growth", "boom")
    assert machine.legal_next_phase("recession") == "recovery"
    assert machine.legal_next_phase("recovery") == "growth"
    assert machine.legal_next_phase("growth") == "boom"
    assert machine.legal_next_phase("boom") == "recession"
    assert machine.legal_previous_phase("boom") == "growth"


def test_legal_transition_allowed_and_illegal_transitions_rejected() -> None:
    machine = load_ordered_cycle_state_machine()

    legal = machine.check_transition("boom", "recession")
    self_transition = machine.check_transition("boom", "boom")
    skip = machine.check_transition("boom", "recovery")
    reverse = machine.check_transition("recession", "boom")

    assert legal.is_legal is True
    assert legal.rejection_reason is None
    assert self_transition.is_legal is False
    assert self_transition.rejection_reason == "self_transition_not_legal_next"
    assert skip.is_legal is False
    assert skip.rejection_reason == "illegal_transition_requires_explicit_override_contract"
    assert reverse.is_legal is False
    assert reverse.rejection_reason == "illegal_transition_requires_explicit_override_contract"


def test_unknown_phase_rejected() -> None:
    machine = load_ordered_cycle_state_machine()

    try:
        machine.legal_next_phase("expansion")
    except OrderedCycleStateMachineError as exc:
        assert "Unknown cycle phase" in str(exc)
    else:
        raise AssertionError("unknown phase should be rejected")


def test_state_machine_summary_hard_gates_pass() -> None:
    summary = load_ordered_cycle_state_machine().summary()

    assert summary["ordered_cycle_state_machine_ready"] is True
    assert summary["legal_cycle_order_valid"] is True
    assert summary["illegal_transition_rejected_count"] > 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["legal_transition_semantics_preserved"] is True
