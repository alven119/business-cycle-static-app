from __future__ import annotations

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
    summarize_book_phase_evidence_rules,
)


def test_book_phase_evidence_rule_registry_complete_and_safe() -> None:
    summary = summarize_book_phase_evidence_rules()

    assert summary["evidence_rule_registry_ready"] is True
    assert summary["rule_registry_row_count"] == summary["economic_role_count"]
    assert summary["rule_without_provenance_count"] == 0
    assert summary["rule_without_abstention_condition_count"] == 0
    assert summary["contextual_example_generalized_count"] == 0
    assert summary["arbitrary_numeric_threshold_count"] == 0
    assert summary["safely_operationalizable_role_count"] > 0


def test_qualitative_and_contextual_rules_do_not_emit_thresholds() -> None:
    rows = build_book_phase_evidence_rule_rows()

    assert all(row["numeric_threshold"] is None for row in rows)
    assert not any(row["rule_source"] == "contaminated_legacy" for row in rows)
    assert not any(row["rule_source"] == "contextual_historical_example" for row in rows)
    blocked = {row["role_id"]: row for row in rows}
    assert blocked["growth_sustainable_inflation_interpretation"][
        "evaluator_status"
    ] == "blocked_rule_semantics"
    assert blocked["boom_consumer_confidence"]["evaluator_status"] == "blocked_data"
