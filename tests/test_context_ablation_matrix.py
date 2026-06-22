from __future__ import annotations

from business_cycle.audits.context_ablation import run_context_ablation_audit


def test_context_ablation_matrix_covers_synthetic_and_strict_complete_dates() -> None:
    summary = run_context_ablation_audit()

    assert summary["context_ablation_matrix_ready"] is True
    assert summary["synthetic_ablation_case_count"] > 0
    assert summary["strict_complete_real_date_ablation_case_count"] == 2
    assert summary["production_context_dependency_measured"] is True
    assert summary["data_only_model_economically_validated"] is False
