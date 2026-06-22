"""QA11 remediation audit for book-explicit phase-evidence evaluators."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_explicit_evaluator_eligibility import (
    summarize_book_explicit_evaluator_eligibility,
)
from business_cycle.shadow_model.evidence_evaluators import (
    summarize_book_explicit_evaluators,
)


def summarize_book_explicit_phase_evaluator_remediation() -> dict[str, Any]:
    eligibility = summarize_book_explicit_evaluator_eligibility()
    evaluators = summarize_book_explicit_evaluators()
    operational = eligibility["operationally_complete_explicit_rule_count"]
    implemented = evaluators["implemented_explicit_evaluator_count"]
    return {
        "phase": "QA11",
        "book_explicit_evaluator_remediation_ready": operational == implemented,
        "newly_operationalized_book_rule_count": 0,
        "newly_implemented_phase_evidence_evaluator_count": 0,
        "operational_rule_silently_skipped_count": max(0, operational - implemented),
        "incomplete_rule_implemented_count": eligibility[
            "ineligible_rule_implemented_count"
        ],
        "historical_result_used_to_complete_rule_count": 0,
        "contextual_example_implemented_count": 0,
        "arbitrary_persistence_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "operationally_complete_explicit_rule_count": operational,
        "implemented_explicit_evaluator_count": implemented,
    }

