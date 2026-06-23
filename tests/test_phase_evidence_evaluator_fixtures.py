from __future__ import annotations

from business_cycle.shadow_model.phase_evidence_evaluators import (
    summarize_phase_evidence_evaluators,
)


def test_phase_evidence_evaluator_fixtures_all_pass() -> None:
    summary = summarize_phase_evidence_evaluators()

    assert summary["evaluator_with_complete_fixture_suite_count"] == summary[
        "implemented_evaluator_count"
    ]
    assert summary["fixture_pass_count"] == summary["fixture_count"]
    assert summary["future_data_violation_count"] == 0
    assert summary["mixed_mode_violation_count"] == 0
    assert summary["smoothing_misclassified_count"] == 0
    assert summary["raw_direction_misclassified_count"] == 0
    assert summary["watch_confirmation_confusion_count"] == 0
    assert summary["modern_extension_core_substitution_count"] == 0
    assert summary["qualitative_rule_emitted_evidence_count"] == 0
