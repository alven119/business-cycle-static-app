from __future__ import annotations

from business_cycle.shadow_model.evidence_evaluators import (
    validate_evidence_evaluator_metamorphic_fixtures,
)


def test_evidence_evaluator_metamorphic_properties_pass() -> None:
    summary = validate_evidence_evaluator_metamorphic_fixtures()

    assert summary["evaluator_metamorphic_tests_ready"] is True
    assert summary["evaluator_fixture_pass_count"] == summary["evaluator_fixture_count"]
    assert summary["monotonicity_violation_count"] == 0
    assert summary["unit_conversion_violation_count"] == 0
    assert summary["insufficient_lookback_not_abstained_count"] == 0
    assert summary["future_data_used_count"] == 0
    assert summary["scenario_specific_behavior_count"] == 0
    assert summary["nondeterministic_output_count"] == 0
