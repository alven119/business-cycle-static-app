from __future__ import annotations

from business_cycle.shadow_model.evidence_evaluators import (
    validate_evidence_evaluator_metamorphic_fixtures,
)


def test_each_implemented_evaluator_has_complete_metamorphic_suite() -> None:
    summary = validate_evidence_evaluator_metamorphic_fixtures()

    assert summary["evaluator_metamorphic_coverage_ready"] is True
    assert summary["evaluator_with_complete_metamorphic_suite_count"] == summary[
        "implemented_evaluator_count"
    ]
    assert summary["metamorphic_fixture_pass_count"] == summary[
        "metamorphic_fixture_count"
    ]
    assert summary["future_data_used_count"] == 0
    assert summary["frequency_semantics_violation_count"] == 0
    assert summary["insufficient_lookback_not_abstained_count"] == 0
