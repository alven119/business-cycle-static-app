from __future__ import annotations

from business_cycle.audits.aggregation_rule_leakage import (
    summarize_aggregation_rule_leakage,
)


def test_aggregation_rule_leakage_guard_has_no_historical_labels() -> None:
    summary = summarize_aggregation_rule_leakage()

    assert summary["aggregation_rule_leakage_guard_ready"] is True
    assert summary["aggregation_rule_scenario_id_reference_count"] == 0
    assert summary["aggregation_rule_historical_date_reference_count"] == 0
    assert summary["aggregation_rule_expected_label_reference_count"] == 0
    assert summary["aggregation_rule_nber_reference_count"] == 0
    assert summary["aggregation_rule_return_metric_reference_count"] == 0
    assert summary["historical_result_used_for_rule_selection_count"] == 0
