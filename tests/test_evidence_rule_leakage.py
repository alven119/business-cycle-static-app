from __future__ import annotations

from business_cycle.audits.evidence_rule_leakage import (
    scan_evidence_rule_text,
    summarize_evidence_rule_leakage,
)


def test_evidence_rule_leakage_guard_has_zero_counts() -> None:
    summary = summarize_evidence_rule_leakage()

    assert summary["evidence_rule_leakage_guard_ready"] is True
    assert summary["scenario_id_reference_count"] == 0
    assert summary["historical_date_reference_count"] == 0
    assert summary["expected_label_reference_count"] == 0
    assert summary["nber_reference_count"] == 0
    assert summary["return_metric_reference_count"] == 0
    assert summary["scenario_branch_count"] == 0
    assert summary["historical_observation_copied_as_threshold_count"] == 0
    assert summary["post_diagnostic_rule_change_without_new_version_count"] == 0
    assert summary["historical_result_used_for_rule_selection_count"] == 0


def test_evidence_rule_leakage_scanner_detects_bad_text() -> None:
    counts = scan_evidence_rule_text(
        "dotcom_bubble 2008-09-30 expected_historical_phase NBER portfolio_return if scenario"
    )

    assert counts["scenario_id_reference_count"] == 1
    assert counts["historical_date_reference_count"] == 1
    assert counts["expected_label_reference_count"] == 1
    assert counts["nber_reference_count"] == 1
    assert counts["return_metric_reference_count"] == 1
    assert counts["scenario_branch_count"] == 1
