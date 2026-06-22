from __future__ import annotations

from business_cycle.audits.evidence_rule_provenance import (
    summarize_evidence_rule_provenance_contract,
)


def test_evidence_rule_provenance_has_no_hidden_or_leaking_rules() -> None:
    summary = summarize_evidence_rule_provenance_contract()

    assert summary["evidence_rule_provenance_ready"] is True
    assert summary["rule_count"] == 40
    assert summary["rule_without_provenance_count"] == 0
    assert summary["numeric_threshold_without_units_count"] == 0
    assert summary["hidden_default_parameter_count"] == 0
    assert summary["contaminated_rule_allowed_for_independent_validation_count"] == 0
    assert summary["contextual_example_generalized_count"] == 0


def test_contaminated_legacy_rules_are_not_in_candidate_freeze() -> None:
    summary = summarize_evidence_rule_provenance_contract()

    assert summary["contaminated_legacy_rule_count"] == 0
    assert all(
        row["allowed_for_independent_validation"] is False
        for row in summary["rules"]
    )
