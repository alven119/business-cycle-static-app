from __future__ import annotations

from business_cycle.shadow_model.aggregation_contract import (
    summarize_shadow_aggregation_rule_contract,
)


def test_shadow_aggregation_rule_contract_has_no_weights_or_thresholds() -> None:
    summary = summarize_shadow_aggregation_rule_contract()

    assert summary["aggregation_schema_preregistered"] is True
    assert summary["numeric_weight_count"] == 0
    assert summary["newly_defined_threshold_count"] == 0
    assert summary["equal_weight_aggregation_count"] == 0
    assert summary["missing_evidence_zero_fill_count"] == 0
    assert summary["unavailable_treated_as_neutral_count"] == 0
    assert summary["raw_transform_used_as_supportive_count"] == 0
    assert summary["historical_label_used_for_rule_selection_count"] == 0
