from __future__ import annotations

from business_cycle.audits.book_faithful_shadow_fixtures import (
    summarize_book_faithful_shadow_model_fixtures,
)


def test_shadow_model_synthetic_fixtures_validate_structure_only() -> None:
    summary = summarize_book_faithful_shadow_model_fixtures()

    assert summary["synthetic_structural_validation_ready"] is True
    assert summary["fixture_count"] == 10
    assert summary["canonical_fixture_pass_count"] == summary["canonical_phase_fixture_count"]
    assert summary["incomplete_fixture_false_complete_count"] == 0
    assert summary["modern_extension_satisfied_core_count"] == 0
    assert summary["context_injection_accepted_count"] == 0
    assert summary["missing_evidence_zero_fill_count"] == 0
    assert summary["formal_candidate_phase_computed"] is False

