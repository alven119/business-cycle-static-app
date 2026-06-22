from __future__ import annotations

from business_cycle.audits.book_explicit_evaluator_eligibility import (
    summarize_book_explicit_evaluator_eligibility,
)


def main() -> None:
    summary = summarize_book_explicit_evaluator_eligibility()
    for key in (
        "phase",
        "explicit_rule_eligibility_ready",
        "explicit_rule_count",
        "operationally_complete_explicit_rule_count",
        "operationally_incomplete_explicit_rule_count",
        "contextual_example_rule_count",
        "qualitative_unquantified_rule_count",
        "implementation_required_rule_count",
        "implemented_explicit_evaluator_count",
        "explicit_rule_silently_skipped_count",
        "ineligible_rule_implemented_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
