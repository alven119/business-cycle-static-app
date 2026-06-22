from __future__ import annotations

from business_cycle.audits.context_dependency_governance import (
    summarize_context_dependency_governance,
)


def test_context_dependency_governance_acknowledges_known_material_dependency() -> None:
    summary = summarize_context_dependency_governance()

    assert summary["production_context_dependency_acknowledged"] is True
    assert summary["dependency_classification"] == "phase_selection"
    assert summary["production_context_decoupling_allowed_now"] is False
    assert summary["production_default_preserved"] is True
    assert summary["context_prior_influence_must_be_disclosed"] is True
    assert summary["mislabeled_context_derived_result_count"] == 0
