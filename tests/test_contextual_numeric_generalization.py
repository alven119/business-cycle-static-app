from __future__ import annotations

from business_cycle.audits.contextual_numeric_generalization import (
    summarize_contextual_numeric_generalization,
)


def test_contextual_250000_is_not_executable_threshold() -> None:
    summary = summarize_contextual_numeric_generalization()

    assert summary["contextual_numeric_guard_ready"] is True
    assert summary["contextual_numeric_value_in_audit_registry_count"] >= 1
    assert summary["contextual_numeric_value_in_test_rejection_count"] >= 1
    assert summary["contextual_numeric_value_in_executable_rule_count"] == 0
    assert summary["contextual_numeric_value_in_default_parameter_count"] == 0
    assert summary["contextual_numeric_generalization_count"] == 0
