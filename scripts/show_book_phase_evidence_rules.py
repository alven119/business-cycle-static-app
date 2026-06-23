from __future__ import annotations

from business_cycle.audits.book_phase_evidence_rules import (
    summarize_book_phase_evidence_rules,
)


def main() -> None:
    summary = summarize_book_phase_evidence_rules()
    for key in (
        "phase",
        "evidence_rule_registry_ready",
        "economic_role_count",
        "rule_registry_row_count",
        "operationally_complete_rule_count",
        "operationally_incomplete_rule_count",
        "qualitative_unresolved_rule_count",
        "contextual_example_rule_count",
        "contaminated_rule_count",
        "rule_without_provenance_count",
        "rule_without_abstention_condition_count",
        "contextual_example_generalized_count",
        "arbitrary_numeric_threshold_count",
        "safely_operationalizable_role_count",
        "genuine_rule_blocked_role_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
