from __future__ import annotations

from business_cycle.cycle_state.declared_phase_registry import (
    load_declared_cycle_state,
    summarize_declared_cycle_state,
)


def test_declared_registry_exposes_boom_without_inference() -> None:
    state = load_declared_cycle_state()

    assert state.declared_current_phase == "boom"
    assert state.declaration_source == "user_declared"
    assert state.declaration_status == "active_research_default"
    assert state.legal_previous_phase == "growth"
    assert state.legal_next_phase == "recession"
    assert state.formal_current_phase_inference_enabled is False
    assert state.candidate_phase_emission_enabled is False
    assert state.current_phase_emission_enabled is False


def test_phase_age_contract_avoids_false_precision_without_start_date() -> None:
    state = load_declared_cycle_state()

    assert state.declared_phase_start_date is None
    assert state.declared_phase_age is None
    assert state.phase_age_status == "unknown_or_user_required"


def test_declared_registry_summary_hard_gates_pass() -> None:
    summary = summarize_declared_cycle_state()

    assert summary["declared_cycle_state_registry_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["phase_age_contract_ready"] is True
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["result"] == "passed"
