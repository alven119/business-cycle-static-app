from __future__ import annotations

from business_cycle.audits import run_context_ablation_audit


def test_context_ablation_detects_external_context_dependency() -> None:
    summary = run_context_ablation_audit()

    assert summary["ablation_case_count"] >= 3
    assert summary["phase_changed_by_context_count"] > 0
    assert summary["confidence_changed_by_context_count"] > 0
    assert summary["stage_hint_context_derived_count"] > 0
    assert summary["external_context_dependency_detected"] is True
    assert summary["data_only_model_validated"] is False
    assert summary["context_ablation_ready"] is True

