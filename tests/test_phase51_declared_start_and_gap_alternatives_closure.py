from __future__ import annotations

from business_cycle.audits.phase51_declared_start_and_gap_alternatives_closure import (
    summarize_phase51_declared_start_and_gap_alternatives_closure,
)


def test_phase51_declared_start_and_gap_alternatives_closure_passes() -> None:
    summarize_phase51_declared_start_and_gap_alternatives_closure.cache_clear()
    summary = summarize_phase51_declared_start_and_gap_alternatives_closure()

    assert summary["result"] == "passed"
    assert summary["phase51_declared_start_and_gap_alternatives_ready"] is True
    assert summary["declared_boom_start_governance_ready"] is True
    assert summary["macro_gap_alternative_registry_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["user_confirmation_required"] is True
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["gap_role_count"] >= 30
    assert (
        summary["gap_with_alternative_candidate_count"]
        == summary["gap_role_count"]
    )
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["next_recommended_phase"] == (
        "Phase52_official_macro_source_adapter_wiring"
    )
