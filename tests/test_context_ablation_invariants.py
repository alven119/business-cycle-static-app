from __future__ import annotations

from business_cycle.audits.context_ablation import run_context_ablation_audit


def test_ablation_invariants_hold_for_data_only_and_display_layers() -> None:
    summary = run_context_ablation_audit()

    assert summary["data_only_context_mutation_change_count"] == 0
    assert summary["display_hint_decision_change_count"] == 0
    assert summary["hidden_context_dependency_count"] == 0
    assert summary["provenance_incomplete_case_count"] == 0
    assert summary["model_history_decision_change_count"] > 0
