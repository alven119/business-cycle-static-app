from __future__ import annotations

from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


def test_validation_label_policy_blocks_runtime_and_tuning_use() -> None:
    summary = summarize_validation_label_policy()

    assert summary["validation_label_policy_ready"] is True
    assert summary["label_source_count"] > 0
    assert summary["label_provenance_complete"] is True
    assert summary["label_runtime_usage_prohibited"] is True
    assert summary["label_tuning_usage_prohibited"] is True
    assert summary["scenario_specific_threshold_change_prohibited"] is True
    assert summary["nber_dates_label_source_only"] is True
    assert summary["book_examples_traceability_only"] is True
    assert summary["portfolio_returns_prohibited_as_rule_source"] is True
    assert summary["label_source_without_provenance_count"] == 0
    assert summary["label_runtime_usage_violation_count"] == 0
    assert summary["label_tuning_usage_violation_count"] == 0
    assert summary["scenario_threshold_change_violation_count"] == 0
    assert summary["portfolio_return_rule_source_violation_count"] == 0
    assert summary["sources_missing_required_prohibition_count"] == 0
