from __future__ import annotations

from business_cycle.cycle_state.declared_boom_start_governance import (
    build_declared_boom_start_governance,
    summarize_declared_boom_start_governance,
)


def test_declared_boom_start_governance_passes_without_registry_write() -> None:
    summary = summarize_declared_boom_start_governance()

    assert summary["result"] == "passed"
    assert summary["declared_boom_start_governance_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["governed_confirmation_option_count"] >= 3
    assert summary["user_confirmation_required"] is True
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_declared_boom_start_governance_contains_no_prohibited_outputs() -> None:
    artifact = build_declared_boom_start_governance()

    assert artifact["prohibited_output_field_count"] == 0
    assert artifact["standalone_classifier_added_count"] == 0
    assert artifact["phase_rank_or_score_added_count"] == 0
    assert artifact["production_behavior_change_count"] == 0
