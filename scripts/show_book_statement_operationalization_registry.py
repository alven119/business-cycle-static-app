from __future__ import annotations

from business_cycle.audits.book_statement_operationalization import (
    summarize_book_statement_operationalization_registry,
)


def main() -> None:
    summary = summarize_book_statement_operationalization_registry()
    for key in (
        "phase",
        "book_statement_operationalization_ready",
        "statement_count",
        "universal_rule_count",
        "directional_rule_count",
        "smoothing_rule_count",
        "persistence_rule_count",
        "contextual_example_count",
        "qualitative_unquantified_count",
        "contextual_example_used_as_universal_rule_count",
        "qualitative_statement_given_arbitrary_threshold_count",
        "statement_without_source_provenance_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
