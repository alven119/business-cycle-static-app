from __future__ import annotations

import inspect

from business_cycle.phases.data_only_resolver import resolve_phase_data_only


def test_data_only_resolver_signature_has_no_external_context_parameters() -> None:
    forbidden = {
        "cycle_context",
        "baseline_phase_id",
        "baseline_stage_note_zh",
        "baseline_reason_zh",
        "display_hint",
        "dashboard_label",
    }

    assert forbidden.isdisjoint(inspect.signature(resolve_phase_data_only).parameters)


def test_context_mutation_does_not_change_data_only_result() -> None:
    scores = {"recession": 20, "recovery": 30, "growth": 88, "boom": 45}

    first = resolve_phase_data_only(scores, previous_model_phase="recovery")
    second = resolve_phase_data_only(scores, previous_model_phase="recovery")

    assert first.decision.current_phase_id == second.decision.current_phase_id
    assert first.metadata["external_context_used"] is False
    assert first.metadata["display_hint_used"] is False
    assert first.metadata["previous_phase_source"] == "model_state_history"


def test_model_history_can_change_sequence_constrained_decision() -> None:
    scores = {"recession": 92, "recovery": 62, "growth": 55, "boom": 30}

    no_history = resolve_phase_data_only(scores)
    recovery_history = resolve_phase_data_only(scores, previous_model_phase="recovery")

    assert no_history.decision.current_phase_id != recovery_history.decision.current_phase_id
    assert recovery_history.metadata["sequence_constraint_applied"] is True
